"""
Dataclasses representing per-track and per-release info
"""

import dataclasses

@dataclasses.dataclass()
class TrackInfo:
	"""Basic metadata for a track"""

	artist:str
	"""Artist name"""

	album:str
	"""Release name"""

	title:str
	"""Track title"""

	track_number:int
	"""Track number"""

	disc_number:int
	"""Disc number"""

	year:str|None
	"""Year (if available)"""

	duration:float
	"""Track duration (seconds)"""

	@property
	def duration_formatted(self) -> str:
		"""String-formatted duration (mm:ss)"""
		return f"{str(round(self.duration // 60)).zfill(2)}:{str(round(self.duration%60)).zfill(2)}"

@dataclasses.dataclass()
class ReleaseInfo:
	"""Release info for a collection of tracks"""

	tracks:list[TrackInfo]
	"""A list of track info"""

	@property
	def artists(self) -> list[str]:
		"""A list of all track artists in this release"""

		return list(set(track.artist for track in self.tracks))
	
	@property
	def artist_formatted(self) -> str:
		"""String-formatted artist, or Various Artists if multiple"""

		if self.is_various_artists:
			return "Various Artists"
		else:
			return self.artists[0]
	
	@property
	def is_various_artists(self) -> bool:
		"""Release is considered Various Artists track artists differ between tracks"""

		return len(self.artists) > 1
	
	@property
	def album(self) -> str:
		"""Release name"""

		return self.tracks[0].album
	
	@property
	def years(self) -> list[str]:
		"""Years from tracks"""

		return sorted(set(t.year for t in self.tracks if t is not None))
	
	@property
	def years_formatted(self) -> str|None:
		"""String-formatted year, or range of years if more than one across tracks"""

		if len(self.years) > 1:
			return f"{self.years[0]} - {self.years[-1]}"
		elif not self.years:
			return None
		else:
			return self.years[0]
	
	@property
	def discs(self) -> list[int]:
		"""Disc numbers found across tracks"""
		return sorted(list(set(track.disc_number for track in self.tracks)))
	
	@property
	def is_multiple_discs(self) -> bool:
		"""Multiple discs if disc numbers are different across tracks"""
		return len(self.discs) > 1
	
	@property
	def duration(self) -> float:
		"""Total duration of the release (seconds)"""
		return sum(t.duration for t in self.tracks)
	
	@property
	def duration_formatted(self) -> str:
		"""String-formatted duration (mm:ss)"""
		return f"{str(round(self.duration // 60)).zfill(2)}:{str(round(self.duration%60)).zfill(2)}"