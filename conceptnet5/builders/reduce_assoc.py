"""
Implements the `reduce_assoc` builder, which filters a tab-separated list of
associations.
"""

from collections import defaultdict

from conceptnet5.relations import is_negative_relation
from conceptnet5.uri import is_concept, uri_prefix


def concept_is_bad(uri):
    """
    Skip concepts that are unlikely to be useful.

    A concept containing too many underscores is probably a long, overly
    specific phrase, possibly mis-parsed. A concept with a colon is probably
    detritus from a wiki.
    """
    return (':' in uri or uri.count('_') >= 3 or
            uri.startswith('/a/') or uri.count('/') <= 2)


def reduce_assoc(filename, output_filename, cutoff=3, en_cutoff=3):
    """
    Takes in a file of tab-separated simple associations, and removes
    uncommon associations and associations unlikely to be useful.

    All concepts that occur fewer than `cutoff` times will be removed.
    All English concepts that occur fewer than `en_cutoff` times will be removed.
    """
    counts = defaultdict(int)
    with open(filename, encoding='utf-8') as file:
        for line in file:
            left, right, _value, _dataset, rel = line.rstrip().split('\t')
            if rel == '/r/SenseOf':
                pass
            else:
                gleft = uri_prefix(left)
                gright = uri_prefix(right)
                if is_concept(gright):
                    counts[gleft] += 1
                if is_concept(gleft):
                    counts[gright] += 1

    filtered_concepts = {
        concept for (concept, count) in counts.items()
        if (
            count >= en_cutoff or
            (not is_concept(concept) and count >= cutoff)
        )
    }

    with open(output_filename, 'w', encoding='utf-8') as out:
        with open(filename, encoding='utf-8') as file:
            for line in file:
                left, right, value, dataset, rel = line.rstrip().split('\t', 4)
                if concept_is_bad(left) or concept_is_bad(right) or is_negative_relation(rel):
                    continue
                fvalue = float(value)
                gleft = uri_prefix(left)
                gright = uri_prefix(right)
                if (
                    gleft in filtered_concepts and
                    gright in filtered_concepts and
                    fvalue != 0
                ):
                    if gleft != gright:
                        line = '\t'.join([gleft, gright, value, dataset, rel])
                        print(line, file=out)

