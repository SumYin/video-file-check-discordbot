# video-file-check-discordbot

A Discord bot to validate and check video file specifications for Discord communities.

This bot was created with the intention of providing Discord servers that see many file submissions from its community (for a contest, for instance) an applicaiton which gives its users a convenient way of checking their files' properties against the bot host's specifications.
This bot is meant to be self-hosted.

This bot takes either a file attachment or a url as a file input, reads the file using ffprobe, and outputs the file's:

- name
- size (MB)
- format
- resolution (HxV)
- frame count
- frame rate
- codec

It compares these values to a set of host-defined target values, in order to validate whether the file suits the server's standards.

Additionally, in the context of a contest, hosts can specify their own 'rules' and 'FAQs' for users to query through the bot, making this information easily accessible to them.

## Commands

`/check_file [attachment]`: upload an attachment, have it analyzed, and recieve an output of the file's properties along with their validation. The file is subject to Discord's file size limitations.

`/check_link [url]`: send a file through a link, have it analyzed, and recieve an output of the file's properties along with their validation. The file is not subject to Discord's file size limitations.

`/rules`: request the host-defined rules.

`/faq`: request the host-defined FAQs.

`/ping`: test ping.

## Setup

1. Install Python (developed with `3.10.6`).
2. Install dependencies, `pip install -r requirements.exe`.
3. Acquire and place `ffprobe.exe` in the root directory.
4. Create a `videos` folder in root directory.
5. To run application, place your Discord bot token in an `.env` file in the root directory.
6. For testing of different media, create a `test-data` folder in root directory and place test media in it.
7. Modify properties in the `host.json` file as desired.

## host.json

This file contains properties defined by the host. These are:

#### rules_title

Title of rules section.

#### rules

Array of strings, each defining a rule of a contest or competition.

#### faq_title

Title of FAQ section.

#### faq

Array of objects, each containting 2 strings: a question, and an answer.
Useful for more FAQ formatted rules.

#### targets

Set of objects defining the target values expected of the user-uploaded files.

There is an array for each respective property analyzed from the user file (size, format, fps, etc.), allowing for multiple valid target values (for a submission process that accepts both `.mp4` and `.mov` files, for example).
If a file's property matches _one_ of those array values, that property is considered to be valid.

#### cooldown_times

Object containing properties related to rate-limiting (per-user).

It holds two objects, a `short` and `long` cooldown property set, each holding a `tokens` and `period` property.
`tokens` defines how many times a user can execute a command in a given `period` (seconds) before being rate-limited.

For example, `tokens: 3, period: 20` means that a user can execute 3 commands in 20 seconds before rate-limiting begins.
After a period of 20 seconds, the rate-limiting resets.

The `short` cooldown property set is used for cheap commands, while the `long` cooldown property set is used for commands that download and analyze files.

#### limits

Object which contains limit values for file uploads:

- `max_upload_size`, which defines the maximum file size (MB) for a user upload.
- `max_upload_time`, which defines the maximum time (seconds) an upload is allowed to last (i.e. a timeout).

This is useful for url file uploads which may far exceed Discord's upload limitations.

## Disclaimers

**As a host**, you are downloading users' files onto your hosting machine to analyze them.
Files are stored in the root directory `videos` folder, and are deleted immediately after the bot has finished outputting its response to the user.
In the event of a bot crash, it is possible that the program will not have the chance to delete the contents of this folder.
In the event of many concurrent users, your server's network will be impacted as it attempts to download all of its users' files.
The maximum file size users can upload is limited only by the `max_upload_size` value in `host.json` (or Discord's file upload limit, in the case of attachments).
Setting this very high will allow users to upload very large files.

**As a user**, you are uploading your file to the bot host's server.
Despite the program deleting your file, there is no guarantee the host cannot deliberately copy your file or stop the program in order to retain your file.
Your files are not encrypted by this program.
If your files are meant to be confidential, this program cannot guarantee they will not be seen or kept by the bot host.