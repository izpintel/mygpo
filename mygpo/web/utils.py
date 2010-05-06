from mygpo.api.models import Podcast, EpisodeAction
from babel import Locale, UnknownLocaleError
import re

def get_accepted_lang(request):
    return list(set([s[:2] for s in request.META.get('HTTP_ACCEPT_LANGUAGE', '').split(',')]))

def get_podcast_languages():
    """
    Returns all 2-letter language codes that are used by podcasts.

    It filters obviously invalid strings, but does not check if any
    of these codes is contained in ISO 639.
    """

    langs = [x['language'] for x in Podcast.objects.values('language').distinct()]
    sane_lang = sanitize_language_codes(langs)

    sane_lang.sort()

    return sane_lang


def sanitize_language_codes(langs):
    """
    expects a list of language codes and returns a unique lost of the first
    part of all items. obviously invalid entries are skipped

    >>> sanitize_language_codes(['de-at', 'de-ch'])
    ['de']

    >>> sanitize_language_codes(['de-at', 'en', 'en-gb', '(asdf', 'Deutsch'])
    ['de', 'en]
    """

    r = '^[a-zA-Z]{2}[-_]?.*$'
    return list(set([l[:2] for l in langs if l and re.match(r, l)]))


def get_language_names(lang):
    """
    Takes a list of language codes and returns a list of tuples
    with (code, name)
    """
    res = {}
    for l in lang:
        try:
            locale = Locale(l)
        except UnknownLocaleError:
            continue

        if locale.display_name:
            res[l] = locale.display_name

    return res


class UpdatedException(Exception):
    """Base exception with additional payload"""
    def __init__(self, data):
        Exception.__init__(self)
        self.data = data


def get_played_parts(user, episode):
    """
    return a list of length of alternating unplayed, played parts of the given
    episode for the given user and the resulting duration of the episode

    If no information is available, None and the stored duration of the episode
    are returned
    """
    actions = EpisodeAction.objects.filter(episode=episode, user=user, action='play', playmark__isnull=False, started__isnull=False)

    if actions.count() == 0:
        return None, episode.duration

    lengths = [x.total for x in actions]
    median_length = lengths[len(lengths)/2]

    # flatten (merge) all play-parts
    played_parts = flatten_intervals(actions)

    # if end of last played part exceeds median length, extend episode
    length = max(median_length, played_parts[len(played_parts)-1]['end'])

    #split up the played parts in alternating 'unplayed' and 'played'
    #sections, starting with an unplayed
    sections = []

    lastpos = 0
    for played_part in played_parts:
        sections.append(played_part['start'] - lastpos)
        sections.append(played_part['end'] - played_part['start'])
        lastpos = played_part['end']

    intsections = [int(s) for s in sections]

    return intsections, length


def flatten_intervals(actions):
    """
    takes a list of EpisodeActions and returns a sorted
    list of hashtables with start end elements of the flattened
    play intervals.
    """
    actions = filter(lambda x: x.started and x.playmark, actions)
    actions.sort(key=lambda x: x.started)
    played_parts = []
    first = actions[0]
    flat_date = {'start': first.started, 'end': first.playmark}
    for action in actions:
        if action.started <= flat_date['end'] and action.playmark >= flat_date['end']:
            flat_date['end'] = action.playmark
        elif action.started >= flat_date['start'] and action.playmark <= flat_date['end']:
            # part already contained
            continue
        else:
            played_parts.append(flat_date)
            flat_date = {'start': action.started, 'end': action.playmark}
    played_parts.append(flat_date)
    return played_parts

