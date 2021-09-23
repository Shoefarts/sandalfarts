# Sandalfarts

A Discord bot for Wynncraft-related utility commands coded in Python for private use.


## Usage

All commands are prefixed with `:sh` with a space following after.

### XP Competition

Commands in this category pertain to Nerfurian Guild XP competition tracking.

  - `xpcomp` will display a live leaderboard of players ranked from most XP contributed to least.
  - `xpinit` will wipe the leaderboard rankings and start a new XP competition (hardcoded only for use by Shoefarts).

### Guild Wars

Commands in this category are meant for use to access additional data about guild territories and run guild economy calculations.

  - `terrinfo [TERRITORY NAME]` will show data on a specified territory including production information, bordering territories, treasury level, and current territory holder.
  - `guildterr [GUILD NAME]` will return a list of all territories held by the specified guild and their treasury levels in order from oldest to newest.
  - `hqrecommend [GUILD NAME]` will return the territory that has the highest HQ connection bonus, calculated from all the current territories that the specified guild is holding.

### Clown Town Express

Commands in this category are purely for fun and are 100% opt-in with the option to opt-out at any time.

  - `clownparty` will initiate a "boarding party" where users who react to the generated embed in the minute following the command call, will be added to a list of users who will have clown emojis reacted onto all of their messages (only usable by admins).
  - `takemetoclowntown` will add the user who called the command to the list of users to be watched.
  - `getmeoffthistrain` will remove the user who called the command from the list of users being watched.
