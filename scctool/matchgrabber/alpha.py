"""Provide match grabber for AlphaTL."""

import logging
from urllib.request import urlopen, urlretrieve

import scctool.settings
from scctool.matchgrabber.custom import MatchGrabber as MatchGrabberParent

# create logger
module_logger = logging.getLogger('scctool.matchgrabber.alpha')


class MatchGrabber(MatchGrabberParent):
    """Grabs match data from Alpha SC2 Teamleague."""

    _provider = "AlphaSC2"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._urlprefix = "https://alpha.tl/match/"
        self._apiprefix = "https://alpha.tl/api?match="

    def grabData(self, metaChange=False, logoManager=None):
        """Grab match data."""
        data = self._getJson()

        if(data['code'] != 200):
            msg = 'API-Error: ' + data['error']
            raise ValueError(msg)
        else:
            self._rawData = data
            overwrite = (metaChange or
                         self._matchData.getURL().strip() !=
                         self.getURL().strip())
            with self._matchData.emitLock(overwrite,
                                          self._matchData.metaChangedSignal):
                self._matchData.setNoSets(5, resetPlayers=overwrite)
                self._matchData.setMinSets(3)
                self._matchData.setSolo(False)
                self._matchData.resetLabels()
                if overwrite:
                    self._matchData.resetSwap()

                league = data['tournament']
                if not isinstance(league, str):
                    league = "TBD"
                league = league.replace('Non-pro', 'Non-Pro')
                league = league.replace('Semi-pro', 'Semi-Pro')
                self._matchData.setLeague(league)

                for idx, map in enumerate(data['maps']):
                    if not isinstance(map, str):
                        map = "TBD"
                    self._matchData.setMap(idx, map)

                self._matchData.setLabel(4, "Ace Map")
                self._matchData.setAce(4, True)

                for team_idx in range(2):
                    for set_idx, player in enumerate(data['lineup' +
                                                          str(team_idx + 1)]):
                        try:
                            playername = self._aliasPlayer(player['nickname'])
                            if not isinstance(playername, str):
                                playername = "TBD"
                            self._matchData.setPlayer(
                                self._matchData.getSwappedIdx(team_idx),
                                set_idx,
                                playername, str(player['race']))
                        except Exception:
                            self._matchData.setPlayer(
                                self._matchData.getSwappedIdx(team_idx),
                                set_idx, 'TBD', 'Random')

                    team = data['team' + str(team_idx + 1)]
                    name, tag = team['name'], team['tag']
                    if not isinstance(name, str):
                        name = "TBD"
                    if not isinstance(tag, str):
                        tag = ""
                    self._matchData.setTeam(
                        self._matchData.getSwappedIdx(team_idx),
                        self._aliasTeam(name), tag)

                for set_idx in range(5):
                    try:
                        score = int(data['games'][set_idx]) * 2 - 3
                    except Exception:
                        score = 0

                    self._matchData.setMapScore(
                        set_idx, score, overwrite, True)

                self._matchData.setAllKill(False)
                if logoManager is not None:
                    self.downloadLogos(logoManager)
                self._matchData.autoSetMyTeam(
                    swap=scctool.settings.config.parser.getboolean(
                        "SCT", "swap_myteam"))

    def downloadLogos(self, logoManager):
        """Download team logos."""
        if self._rawData is None:
            raise ValueError(
                "Error: No raw data.")

        for idx in range(2):
            try:
                logo_idx = self._matchData.getSwappedIdx(idx) + 1
                oldLogo = getattr(logoManager, 'getTeam{}'.format(logo_idx))()
                logo = logoManager.newLogo()
                url = self._rawData['team' + str(idx + 1)]['logo']
                if url:
                    new_logo = logo.fromURL(
                        self._rawData['team' + str(idx + 1)]['logo'],
                        localFile=oldLogo.getAbsFile())
                    if new_logo:
                        getattr(logoManager,
                                'setTeam{}Logo'.format(logo_idx))(logo)
                    else:
                        module_logger.info("Logo download is not needed.")

            except Exception as e:
                module_logger.exception("message")

    def downloadBanner(self):
        """Download team logos."""
        dir = scctool.settings.casting_data_dir
        transparent = scctool.settings.config.parser.getboolean(
            "SCT", "transparent_match_banner")

        if self._rawData is None:
            raise ValueError(
                "Error: No raw data.")

        fname = dir + "/matchbanner.png"
        url = "https://alpha.tl/announcement/"\
            + str(self.getID())

        if transparent:
            url = url + "?transparent"
        else:
            url = url + "?vs"

        localFile = scctool.settings.getAbsPath(fname)
        needs_download = True
        try:
            with open(localFile, "rb") as in_file:
                local_byte = in_file.read(512)

            file = urlopen(url)
            data = file.read(512)

            if(data == local_byte):
                needs_download = False
        except FileNotFoundError as e:
            pass
        except Exception as e:
            module_logger.exception("message")

        if needs_download:
            try:
                urlretrieve(url, scctool.settings.getAbsPath(fname))

            except Exception as e:
                module_logger.exception("message")
