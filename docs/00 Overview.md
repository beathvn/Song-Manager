# Song-Manager at a glance

Song-Manager supports the following music-library features:

| # | Feature | Status |
| --- | --- | --- |
| 1 | Discover and acquire tracks from Spotify | Operational |
| 2 | Prepare the DJ library in Rekordbox | Manual |
| 3 | Distribute the library across devices | Operational |
| 4 | Refresh secondary-library metadata | Manual |
| 5 | Migrate legacy Rekordbox XML | Manual / legacy |
| 6 | Export a Rekordbox track list | Operational |
| 7 | Review Rekordbox library data quality | Research only |
| 8 | Normalize selected Rekordbox tracks | Experimental / research |
| 9 | Analyze and curate the Rekordbox library | Research only |

## Core workflows

### 1. Discover and acquire tracks

```mermaid
flowchart LR
    Sources[Saved tracks + configured playlists and artists] --> Discovery[Discover candidates]
    Discovery --> NewArrivals[Dated New Arrivals playlist]
    NewArrivals --> Review[Listen and review]
    Review --> Curated[Reusable curated playlist]
    Curated --> Download[Download audio + export CSV]
```

The discovery service reads saved tracks and user-configured playlists and artists. It creates a dated **New arrivals YYYY-MM-DD** playlist from newly found playlist and artist tracks; saved tracks update the local history but are not included in that playlist. Promising tracks are manually added to a user-chosen curated playlist, which is then downloaded. The intended workflow reuses that playlist so its Spotify identifier stays stable in local configuration while its tracks change. The maintainer's playlist is called **Found on the Road**; other users can choose any name.

**Responsible services:** `spotify_discovery`, `spotify_downloader`  
**Status:** Operational — both have launchers.

### 2. Prepare the DJ library

```mermaid
flowchart LR
    Download[Downloaded audio] --> Import[Manual Rekordbox import]
    Import --> Prepare[Analyze and prepare tracks]
    Prepare --> XML[Export Rekordbox XML snapshot]
```

There is no automated hand-off between Spotify and Rekordbox; the user chooses and imports the downloaded audio.

**Responsible:** Rekordbox and the user  
**Status:** Manual — Song-Manager does not automate importing or preparation.

### 3. Distribute the primary library

```mermaid
flowchart LR
    Primary[Primary library: authoritative] --> Export[Export current XML]
    Primary --> Mirror[Mirror audio folders]
    Export --> Mirror
    Mirror --> NewTracks[Import newly added tracks]
    NewTracks --> Secondary[Secondary library]
```

The primary library is authoritative for the music library and its metadata. Before distributing music to a secondary library, export the current primary library XML. Folder synchronization mirrors primary audio and XML folders to the destination, including removal of audio files no longer present in the primary library. Newly added tracks are then imported manually into the secondary library.

**Responsible service:** `rekordbox_syncer`<br>
**Status:** Folder mirroring and XML path rewriting are operational. Importing new tracks into the secondary library remains manual.

### 4. Refresh secondary-library metadata

```mermaid
flowchart LR
    PrimaryXML[Current primary XML] --> Compare[Compare XML snapshots]
    SecondaryXML[Current secondary XML] --> Compare
    Compare --> Updates[Reimport changed tracks]
    Compare --> Removals[Remove obsolete entries]
    Updates --> Secondary[Secondary library]
    Removals --> Secondary
```

Compare current primary and secondary XML snapshots to identify configured metadata changes on tracks already in the secondary library. The report also identifies secondary-library entries that no longer exist in the primary XML. The user manually reimports changed tracks or removes obsolete entries in the secondary library. Every reported action is performed in the secondary library; the primary library is not modified.

Newly added tracks are intentionally excluded because they are handled by the distribution workflow. The comparison fields are configurable, and the two XML snapshots must use the same track location prefix. DJ play count is intentionally ignored: the recommended reimport on the secondary library could otherwise update a newer play-count value incorrectly. A separate planned workflow will correct DJ play counts in the primary library from XML snapshots.

Just so you know: for some changes, the plan will tell you to delete and reimport. This is when f.ex. the underlaying audio file changed, and only a reimport will not properly do it (as the waveform and stuff won't update).

**Responsible service:** `rekordbox_syncer`<br>
**Status:** Manual comparison and action workflow; automated updates are not implemented.

### 5. Migrate legacy Rekordbox XML

```mermaid
flowchart LR
    XML5[Rekordbox 5 XML] --> Migrate[Copy selected metadata]
    XML6[Rekordbox 6 XML] --> Migrate
    Migrate --> Updated[Updated Rekordbox 6 XML]
```

**Responsible service:** `rekordbox_migration`
**Status:** Rekordbox 5 → 6 migration is legacy/manual.

### 6. Export a Rekordbox track list

```mermaid
flowchart LR
    XML[Rekordbox XML snapshot] --> TrackList[Export track title and artist list]
```

**Responsible service:** `rekordbox_maintenance`

| Name | State | Description |
| --- | --- | --- |
| Export track list | Operational | Exports a sorted title/artist list as CSV, PDF, or Excel. |

### 7. Review Rekordbox library data quality

```mermaid
flowchart LR
    XML[Rekordbox XML snapshot] --> Duplicates[Check duplicate file locations]
```

**Responsible service:** `rekordbox_maintenance`

| Name | State | Description |
| --- | --- | --- |
| Data quality checks | Research only | `research/20_rekordbox_data_quality_review.ipynb` currently checks duplicate `@Location` values in the latest Rekordbox 7 XML export. Future checks will cover metadata consistency, completeness, and validity. |
| Correct primary-library DJ play counts | Planned | Will plan corrections from XML snapshots; no workflow or script exists yet. |

### 8. Normalize selected Rekordbox tracks

```mermaid
flowchart LR
    XML[Rekordbox XML snapshot] --> Select[Select tracks marked as quiet]
    Select --> Stage[Copy audio to a staging folder]
    Stage --> Normalize[Normalize audio]
    Normalize --> Review[Manually review and replace tracks]
```

`research/30_normalize_audio.ipynb` contains exploratory local-path code that selects tracks whose Rekordbox comments contain the quiet-track keyword, copies their files to a staging folder, and normalizes the staged audio. There is no maintained command or Finder launcher. The final replacement and any Rekordbox location update remain manual.

**Responsible service:** `rekordbox_maintenance`<br>
**Status:** Experimental / research only.

### 9. Analyze and curate the Rekordbox library

```mermaid
flowchart LR
    XML[Rekordbox XML snapshot] --> Analyze[Explore library distributions]
    Analyze --> Review[Review collection patterns]
    Review --> Curate[Manually refine metadata and collection]
```

`research/90_analyze_rekordbox_library.ipynb` is the current starting point for exploratory library analysis. It currently visualizes the artists most represented in a Rekordbox XML export. This workflow will help identify meaningful patterns in the collection and guide manual curation decisions, such as refining genres, tags, ratings, or playlist placement. It is not a supported Python command or Finder launcher.

**Responsible service:** `rekordbox_maintenance`<br>
**Status:** Research only.

Statuses describe the current code paths, not automated test coverage; the repository does not yet have a dedicated test suite. Last reviewed: **2026-08-28**.

## Detail when needed

Service READMEs contain command-specific setup and troubleshooting. Shared code lives in `libs/`: `spotify_client` holds Spotify models, `rekordbox_client` reads and edits Rekordbox XML, and `song_common` configures logging.
