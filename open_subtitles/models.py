import dataclasses
from typing import Any, List, Self, TypeVar, get_args
from typing_extensions import Annotated, _AnnotatedAlias
from datetime import datetime
from pydantic import RootModel
from pydantic.dataclasses import dataclass, Field

T = TypeVar('T')
Optional = Annotated[T | None, Field(default=None)]


class Default:
	'''
	Annotates field as `Optional[T]` and configures its default value.
	```
	@dataclass
	class MyModel:
	    field_a: Default[str, 'my default value']
	```
	'''

	def __class_getitem__(cls, params):
		if not isinstance(params, tuple):
			params = (params, )

		origin = params[0] | None
		default = params[1]
		metadata = (Field(default=default), *tuple(params[2:]))
		return _AnnotatedAlias(origin, metadata)


@dataclass
class LoginRequest:
	username: str
	password: str


@dataclass
class LoginResponse:
	base_url: Optional[str]
	token: str
	status: int
	user: 'User'


@dataclass
class LogoutResponse:
	message: str
	status: int


@dataclass
class SubtitleSearchRequestParams:
	ai_translated: Default[str, 'exclude']
	machine_translated: Default[str, 'exclude']
	season_number: Optional[int]
	episode_number: Optional[int]
	languages: Optional[str]
	moviehash: Optional[str]
	query: Optional[str]
	page: int


@dataclass
class SubtitleSearchResponse:
	total_pages: int
	total_count: int
	per_page: int
	page: int
	data: List['Subtitle']


@dataclass
class DownloadRequest:
	file_id: int
	sub_format: Optional[str]
	file_name: Optional[str]
	in_fps: Optional[float]
	out_fps: Optional[float]
	timeshift: Optional[float]
	force_download: Optional[bool]


@dataclass
class DownloadResponse:
	link: str
	file_name: str
	requests: int
	remaining: int
	message: str
	reset_time: str
	reset_time_utc: datetime


@dataclass
class User:
	allowed_downloads: int
	allowed_translations: int
	level: str
	user_id: int
	ext_installed: bool
	vip: bool


@dataclass
class Subtitle:
	id: str
	type: str
	attributes: 'SubtitleAttributes'


@dataclass
class SubtitleAttributes:
	subtitle_id: str
	language: str
	download_count: Optional[int]
	new_download_count: Optional[int]
	hearing_impaired: Optional[bool]
	hd: Optional[bool]
	fps: Optional[float]
	votes: Optional[int]
	points: Optional[int]
	ratings: Optional[float]
	from_trusted: Optional[bool]
	foreign_parts_only: Optional[bool]
	ai_translated: Optional[bool]
	machine_translated: Optional[bool]
	upload_date: Optional[str]
	release: Optional[str]
	comments: Optional[str]
	legacy_subtitle_id: Optional[int]
	uploader: Optional['Uploader']
	feature_details: Optional['FeatureDetails']
	url: str
	related_links: Optional[List['RelatedLink']]
	files: List['File']


@dataclass
class File:
	file_id: int
	cd_number: Optional[int]
	file_name: str


@dataclass
class RelatedLink:
	label: Optional[str]
	url: Optional[str]
	img_url: Optional[str]


@dataclass
class Uploader:
	uploader_id: Optional[int]
	name: Optional[str]
	rank: Optional[str]


@dataclass
class FeatureDetails:
	feature_id: int
	feature_type: Optional[str]
	year: Optional[int]
	title: Optional[str]
	movie_name: Optional[str]
	imdb_id: Optional[int]
	tmdb_id: Optional[int]


def serialize(data: any) -> dict | None:
	'''
	Serialize data to a dictionary, preparing it for further low level serialization.
	:If input data is a dictionary, None values are removed.
	:If input data is a model, rules defined on the model, such as default values, are applied.
	'''

	if data is None:
		return None
	elif data and isinstance(data, dict):
		return {k: v for k, v in data.items() if v != None}
	elif dataclasses.is_dataclass(data):
		return RootModel[type(data)](data).model_dump(exclude_none=True)


def deserialize(cls: type, data: dict):
	'''
	Deserialize data from a dictionary into a model specified by patameter cls.
	'''
	return cls(**data)
