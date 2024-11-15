import sys, pathlib, dataclasses, io
import tinytag, musicbrainzngs, torf, alive_progress
from .info import TrackInfo, ReleaseInfo

MEDIA_EXTENSIONS = (".flac",".mp3",".m4a")
"""File extensions to consider"""

def get_info_for_media_file(path_media:str) -> TrackInfo:
	"""Get metadata for a particular media file (track)"""

	tags = tinytag.TinyTag.get(path_media)

	return TrackInfo(
		artist = tags.artist or tags.albumartist,
		album  = tags.album,
		title  = tags.title,
		track_number = tags.track or 0,
		disc_number = tags.disc or 1,
		year = tags.year or None,
		duration = tags.duration
	)

def get_content_info_for_folder(path_folder:str) -> list[ReleaseInfo]:
	"""Find all releases for a given source folder"""

	# Get a bunch of track info
	tracks_info:dict[str, list[TrackInfo]] = {}

	for path_file in pathlib.Path(path_folder).rglob("*"):

		if path_file.name.startswith("."):
#			print("Skipping dotfile", path_file, file=sys.stdout)
			continue

		if path_file.suffix.lower() not in MEDIA_EXTENSIONS:
#			print("Skipping non-media file", path_file)
			continue
		
		try:
			track_info = get_info_for_media_file(str(path_file))
		except Exception as e:
			print(f"x Skipping {path_file}: {e}", file=sys.stderr)
			continue
		
		if track_info.album not in tracks_info:
			tracks_info[track_info.album] = []
		
		tracks_info[track_info.album].append(track_info)
	
	# Sort into releases
	releases:list[ReleaseInfo] = []
	
	for tracks in tracks_info.values():
		releases.append(ReleaseInfo(tracks))
	
	return releases

def write_track_listing(release:ReleaseInfo) -> str:

	str_buffer = io.StringIO()

	print("Artist:   ", release.artist_formatted, file=str_buffer)
	print("Album:    ", release.album, file=str_buffer)
	print("Year:     ", release.years_formatted, file=str_buffer)
	print("Duration: ", release.duration_formatted, file=str_buffer)

	for disc in release.discs:
		print("", file=str_buffer)
		if release.is_multiple_discs:
				print(f"  Disc {disc}", file=str_buffer)
		
		for track in [t for t in sorted(release.tracks, key=lambda x:x.track_number) if t.disc_number == disc]:
			print(f"  {str(track.track_number).zfill(2)}. {track.title} ({str(round(track.duration)//60).zfill(2)}:{str(round(track.duration)%60).zfill(2)})", file=str_buffer)
	
	return str_buffer.getvalue()

def lookup_release_info(release:ReleaseInfo) -> str:
	"""Not so great"""

	musicbrainzngs.set_useragent("orphtor", "0.1", "michael@glowingpixel.com")

	mb_info = musicbrainzngs.search_releases(artist=release.artist_formatted, release=release.album, limit=1)
	print(mb_info)

def prep_torrent(path_source):

	return torf.Torrent(
		path = path_source,
	)

def update_bar(bar:alive_progress.alive_bar, torrent:torf.Torrent, current_file:str, current_hashed:int, total_hashes:int):
	#print(str(current_hashed), "of", str(total_hashes))
	bar.text(current_file)
	bar(current_hashed/total_hashes)


def main(path_source:str) -> str:
	"""Do the whole thing for a source path"""

	# Get content info
	if not pathlib.Path(path_source).is_dir():
		raise ValueError("Source should be a folder")
	
	releases = get_content_info_for_folder(path_source)

	if not releases:
		raise FileNotFoundError("No releases found")

	# Write Orpheus description
	release_descriptions = []
	for release in releases:
		release_descriptions.append(write_track_listing(release))
	
	print("\n\n".join(release_descriptions))
	description_path = pathlib.Path(path_source).with_suffix(".txt")
	with description_path.open("w", encoding="utf-8") as desc:
		desc.write("\n\n".join(release_descriptions))

	# Create torrent file
	torrent = prep_torrent(path_source)
	
	print("Generating torrent...")
	with alive_progress.alive_bar(manual=True, theme="musical") as bar:
		torrent.generate(callback=
			lambda torrent, current_file, current_hashed, total_hashes:
				update_bar(bar, torrent, current_file, current_hashed, total_hashes
		))
	
	output_path = pathlib.Path(path_source).with_suffix(".torrent")
	torrent.write(output_path)
	print("")
	print("Torrent written to", output_path)
	print("")


if len(sys.argv) < 2:
	print(f"Usage: {pathlib.Path(__package__).name} torrent_contents [...]")

for path in sys.argv[1:]:
	try:
		main(path)
	except Exception as e:
		print(f"{path}: {e}")