import functools
import glob
import io
import os
import shutil
import traceback
import requests
import yaml
from typing import Any, Callable, Iterable, TypeVar
from argparse import ArgumentParser
from appdirs import user_config_dir
from braceexpand import braceexpand
from open_subtitles.api import OpenSubtitles
from open_subtitles.models import Subtitle

T = TypeVar('T')
U = TypeVar('U')

keyIndexing = 'qwertzuiopasdfghjklyxcvbnm'


def get_key_for_index(idx: int):
	return keyIndexing[idx] if idx < len(keyIndexing) else ''


def get_index_for_key(key: str):
	return keyIndexing.index(key)


def main(*video_paths: str, app_name: str, api_key: str, username: str = None, password: str = None, languages: Iterable[str] = [], pause=False):
	if not video_paths or not len(video_paths):
		raise ValueError('At least one video path must be provided')

	try:
		api = OpenSubtitles(app_name, api_key)

		selected: dict[str, list[Subtitle]] = {}

		for i, video_path in enumerate(video_paths):
			subtitles = api.search_file(video_path, languages=languages)

			# Filter results based on attributes (bad, translated, ...)
			subtitles = [x for x in subtitles if not x.attributes.ai_translated and not x.attributes.machine_translated]

			# Sort subtitle results by criteria defined in comparer
			subtitles = sorted(subtitles, key=functools.cmp_to_key(lambda a, b: subtitle_comparer(a, b, languages)))
			subtitles: list[Subtitle]

			selected[video_path] = selection_ui(subtitles, video_path)

		login_response = api.login(username, password)
		print(f'Logged in {login_response.user}; status: {login_response.status}; server: {login_response.base_url}\n')

		try:
			for video_path, subtitles in selected.items():
				counter = None if len(subtitles) == 1 else 1

				for subtitle in subtitles:
					subtitle_file = subtitle.attributes.files[0]

					print('Downloading', subtitle_file.file_id, subtitle_file.file_name)

					download_info = api.get_download_link(subtitle_file.file_id)

					# Subtitles are srt, unless explicitly asked for other format when downloading
					baseName, _ = os.path.splitext(video_path)
					subtitle_ext = '.srt'

					if counter is None:
						name = f'{baseName}{subtitle_ext}'
					else:
						name = f'{baseName}.{counter}.{subtitle.attributes.language}{subtitle_ext}'
						counter += 1

					download_file(download_info.link, name)
		finally:
			api.logout()

	except Exception:
		traceback.print_exc()
	finally:
		if pause:
			input('\nPress ENTER to finish...')


def download_file(url: str, file_path: str):
	with requests.get(url, stream=True) as r:
		with open(file_path, 'wb') as file:
			# Note: Inspecting object r or r.raw in debugger corrupts the data stream.
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, file, 4096)
			# for chunk in r.iter_content(4096):
			# 	file.write(chunk)


def fmt(value, width, fillchar=None):
	return str(value).ljust(width, fillchar or ' ')[0:width]


def trunc(value, decimals):
	return int(value * (10**decimals)) / (10**decimals)


def compareByArray(array: list[T], a: U, b: U, selector: Callable[[U], T] = lambda x: x):
	return array.index(selector(a)) - array.index(selector(b))


# sort: language -> from_trusted -> hearing_impaired
def subtitle_comparer(a: Subtitle, b: Subtitle, langs_order: list[str]):
	d = compareByArray(langs_order, a, b, lambda x: x.attributes.language)
	if d != 0:
		return d

	d = b.attributes.from_trusted - a.attributes.from_trusted
	if d != 0:
		return d

	return a.attributes.hearing_impaired - b.attributes.hearing_impaired


def selection_ui(subtitles: list[Subtitle], video: str) -> list[Subtitle]:
	video = os.path.basename(video)

	terminalWidth = shutil.get_terminal_size((80, 20))[0] - 1

	# Key, Subtitle name, Lng, HI, HD, trusted
	columnWidths = [1, 0, 3, 2, 2, 2]
	columnWidths[1] = terminalWidth - sum(columnWidths) - len(columnWidths) * 3 - 1

	def fmtLine(*values):
		return '║ ' + ' │ '.join([fmt(x, columnWidths[i]) for i, x in enumerate(values)]) + ' ║'

	def fmtHorizontalLine(char='─', begin='║', end='║', cross: str = ...):
		if cross is ...:
			cross = char

		if char is cross:
			return begin + (char * (terminalWidth - 2)) + end
		else:
			return begin + (cross.join([fmt(x, columnWidths[i] + 2, char) for i, x in enumerate([''] * len(columnWidths))])) + end

	print()
	print(fmtHorizontalLine('═', '╔', '╗'))
	print(f'║ {fmt("Video: " + video, terminalWidth - 4)} ║')
	print(fmtHorizontalLine('═', '╠', '╣', '╤'))
	print(fmtLine('K', 'Subtitle name', 'Lng', 'HI', 'HD', 'Tr'))
	print(fmtHorizontalLine(begin='╟', cross='┼', end='╢'))

	for j, s in enumerate(subtitles):
		print(
		    fmtLine(
		        get_key_for_index(j),
		        s.attributes.files[0].file_name,
		        s.attributes.language,
		        int(s.attributes.hearing_impaired),
		        int(s.attributes.hd),
		        int(s.attributes.from_trusted),
		    ))

	print(fmtHorizontalLine('═', '╚', '╝', '╧'))

	try:
		if len(subtitles):
			while True:
				line = input('\nSelect subtitles to download: ')

				if line == '-':
					break

				if len(line):
					try:
						return [subtitles[get_index_for_key(x)] for x in dict.fromkeys(line)]
					except (ValueError, IndexError):
						# Wrong letter was entered or valid letter but out of available subs index
						pass
	finally:
		print()

	return []


parser = ArgumentParser()
parser.add_argument('paths', help='paths to movies or directories with movies', nargs='+')
parser.add_argument('--recursive', '-R', dest='recursive', action='store_true', help='search for movies recursively')
parser.add_argument('--languages', '-l', dest='languages', help='comma separated list of language codes to search')
parser.add_argument('--username', '-u', dest='login', help='OpenSubtitles login name')
parser.add_argument('--password', '-p', dest='password', help='OpenSubtitles password')
parser.add_argument('--pause', dest='pause', action='store_true', help='wait for user input on end')
args = parser.parse_args()

# TODO: recursive

expandedPaths = set()
for arg in args.paths:
	if os.path.exists(arg):
		expandedPaths.add(arg)

	for exp in braceexpand(arg, False):
		if os.path.exists(exp):
			expandedPaths.add(exp)

		expandedPaths.update(glob.glob(exp))

# Build optional arguments; it is done this way so we don't have to pass default values manually (usually None or ...)
kwargs = {}

try:
	# This maps to %appdata%\Subleecher\config.yaml and ~/.config/SubLeecher/config.yaml
	config_path = os.path.join(
	    user_config_dir('SubLeecher', appauthor=False, roaming=True),
	    'config.yaml',
	)

	with io.open(config_path, 'rt') as fin:
		config = yaml.safe_load(fin)
except Exception:
	# If the file does not exist or is unreadable
	pass
else:
	if isinstance(config, dict):
		if 'username' in config:
			kwargs['username'] = config['username']
		if 'password' in config:
			kwargs['password'] = config['password']
		if 'languages' in config:
			kwargs['languages'] = config['languages']
		if 'app_name' in config:
			kwargs['app_name'] = config['app_name']
		if 'api_key' in config:
			kwargs['api_key'] = config['api_key']

if args.languages:
	kwargs['languages'] = args.languages

if args.login and args.password:
	kwargs['username'] = args.login
	kwargs['password'] = args.password
elif args.login or args.password:
	parser.error('--username and --password arguments must be used together')

main(*expandedPaths, pause=args.pause, **kwargs)
