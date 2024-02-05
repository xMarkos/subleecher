import os
from typing import Any, Iterable
import requests
from . import oshash
from .models import (
    serialize,
    deserialize,
    Subtitle,
    LoginRequest,
    LoginResponse,
    SubtitleSearchRequestParams,
    SubtitleSearchResponse,
    LogoutResponse,
    DownloadRequest,
    DownloadResponse,
)


class OpenSubtitles(object):
	API_HOST = 'api.opensubtitles.com'

	def __init__(self, app_name: str, api_key: str) -> None:
		self.api_host = self.API_HOST
		self.user_agent = app_name
		self.api_key = api_key

		self._token: str | None = None

	def _request(
	    self,
	    method: str,
	    entity_path: str,
	    query_string: dict[str, str] | Any = None,
	    headers: dict[str, str] | None = None,
	    payload: dict[str, str] | Any = None,
	) -> requests.Response:

		# query_string and payload may be either dict or a model object, but headers must be a dict.
		headers0 = headers
		headers = {
		    'Content-Type': 'application/json',
		    'Accept': 'application/json',
		    'User-Agent': self.user_agent,
		    'Api-Key': self.api_key,
		}

		if self._token:
			headers['Authorization'] = f'Bearer {self._token}'

		if headers0:
			headers |= headers0

		query_string = serialize(query_string)
		headers = serialize(headers)
		payload = serialize(payload)

		return requests.request(
		    method,
		    f'https://{self.api_host}/api/v1/{entity_path}',
		    params=query_string,
		    json=payload,
		    headers=headers,
		)

	def login(self, user_name: str, password: str):
		'''
		Log-in the user with their user name and password.
		Store the token for further use.
		'''

		response = self._request('POST', 'login', payload=LoginRequest(user_name, password))
		response.raise_for_status()

		login_response: LoginResponse = deserialize(LoginResponse, response.json())

		if login_response.base_url:
			self.api_host = login_response.base_url

		self._token = login_response.token
		return login_response

	def logout(self) -> LogoutResponse:
		'''
		Log-out the user.
		'''

		response = self._request('DELETE', 'logout', None, None, None)
		response.raise_for_status()

		self._token = None
		return deserialize(LogoutResponse, response.json())

	def search_file(self, file_path: str, *, languages: Iterable[str] | str = None):
		'''
		Search subtitles from a locally available file.
		'''

		hash = oshash.File(file_path).get_hash()

		return self.search(
		    file_name=os.path.basename(file_path),
		    hash=hash,
		    languages=languages,
		)

	def search(self, *, file_name: str = None, hash: str = None, season: int = None, episode: int = None, languages: Iterable[str] | str = None):
		'''
		Search subtitles.

		:param file_name: Search by 'query'.
		:param hash: Search by OS hash.
		:param season: Search for a season number.
		:param episode: Search for an episode number.
		:param languages: Comma separated string of language codes to search.
		'''

		if len(languages) and not isinstance(languages, str):
			languages = ','.join(languages)

		items: list[Subtitle] = []

		page = 1
		while True:
			response = self._request(
			    'GET', 'subtitles',
			    SubtitleSearchRequestParams(
			        season_number=season,
			        episode_number=episode,
			        languages=languages,
			        moviehash=hash,
			        query=file_name,
			        page=page,
			    ))

			response.raise_for_status()

			search_result: SubtitleSearchResponse = deserialize(SubtitleSearchResponse, response.json())

			items.extend(search_result.data)

			if page >= search_result.total_pages:
				break
			else:
				page += 1

		return items

	def get_download_link(self, file_id: int) -> DownloadResponse:
		'''
		Trigger a download, obtaining a direct link to the resource.
		This action consumes 1 API download point.
		'''

		response = self._request('POST', 'download', payload=DownloadRequest(file_id=file_id))
		response.raise_for_status()

		return deserialize(DownloadResponse, response.json())
