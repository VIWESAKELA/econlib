# -*- coding: utf-8 -*-
"""
============
mappingtools
============

A collection of methods for mapping strings
"""
import re
from math import sqrt
from fuzzywuzzy import process, fuzz

__author__ = """Co-Pierre Georg (co-pierre.georg@uct.ac.za)"""
__version__ = 0.91


class Mapping(object):

    identifier = ""
    from_strings = []  # contains the raw from_strings
    reduced_from_strings = {}  # contains the reduced from_strings with unique entries and relative frequencies
    mapping_original_standardized_from_strings = {}  # contains the original string as key and the corresponding standardized string as value

    # NOTE: this variable is not always needed, e.g. when there is only one input file but with multiple
    #       occurences of certain strings. in this case the mapping is not between files, but from the various
    #       forms a given string is written to it's unique (correct) form
    to_string_array = []  # contains the raw to_strings
    to_string_dict = {}  # contains the reduced to_strings with unique entries and relative frequencies

    def __init__(self):
        pass

    def tuple_to_string(self, t):
        """
        Wrapper for '_'.join method.

        Parameters
        ----------
        t: tuple (or list) to be transformed(tuple)

        Returns
        -------
        the string corresponding to the tuple with "_" between entries of the tuple
        """
        return '_'.join(t)

    def read_redundant_strings(self, redundant_strings_file_name):
        """
        This file reads redundant strings into an array.

        Parameters
        ----------
        redundant_strings_file_name: file name

        Returns
        -------
        List of redundant_strings.
        """

        redundant_strings = []
        # read redundant strings from file.
        with open(redundant_strings_file_name, 'r') as f:
            for line in f.readlines():
                redundant_strings.append(line.strip())
                # we also remove the upper case version of each string
                redundant_strings.append(line.strip().upper())
        return redundant_strings

    def standardize_string(self, original_string, redundant_strings):
        """
        Take an original string and standardize it by stripping special characters and redundant strings.

        Parameters
        ----------
        original_string: string to be standardized
        redundant_strings_file_name: the file where redundant strings (one per line) are listed

        Returns
        -------
        Standardized string without special characters and redundant strings.

        Note:
        - The redundant_strings_file contains strings that can be stripped from the strings that are being parsed.
          Examples: 'the', 'of'
        - Each string in the redundant_strings_file is in a single line
        - The uppercase version of each redundant string is also automatically removed
        """
        # all in upper case letters
        original_string = original_string.upper().strip()

        # special characters should be removed from all strings
        special_characters = "/,\'“”\?\.\"-"
        for special_character in special_characters:
            original_string = original_string.replace(special_character, "")

        # replace whitespace
        original_string = original_string.replace(" ", "")

        # actually remove redundant strings
        for redundant_string in redundant_strings:
            original_string = re.sub(redundant_string, '', original_string)

        return original_string


    def compute_string_frequency(self, string_array):
        """
        Compute the absolute frequency of every string in a string_array.

        Parameters
        ----------
        string_array: array containing strings, possibly more than once (list)

        Returns
        -------
        Dictionary object containing unique string as key and frequency as value

        Note
        ----
        Absolute frequency is the number of occurences of a unique string.
        This method takes any hashable object and computes the frequency, including tuples.
        """
        from collections import Counter
        return Counter(string_array)

    def find_best_match(self, matching_string, original_strings,
                        number_of_fuzzy_options, threshold_fuzziness,
                        debug=None):
        """
        Find the best match of a string in an array of strings.

        Parameters
        ----------
        matching_string: the string that is to be matched
        original_strings: the list of strings from which the best match is to be found
        number_of_fuzzy_options: the number of alternatives of the matching_string fuzzywuzzy should find in the original_strings
        threshold_fuzziness: the lower threshold for the precision of fuzzy matches

        Returns
        -------
        String with best match to matching_string in original_strings.
        """
        # the possible matches are the original_strings array reduced by the
        # string we are trying to match
        reduced_original_strings = list(original_strings)
        reduced_original_strings.remove(matching_string)

        # find fuzzy matches in the reduced list of all entries
        matching_options = process.extract(
            matching_string,
            reduced_original_strings,
            limit=number_of_fuzzy_options
        )

        # we start with the original string
        original_frequency = original_strings[matching_string]
        best_match_precision = 0.0  # original string is not in the reduced list of all entries
        best_match = matching_string

        # the best matching option is found by checking fuzziness and relative frequency of all matches
        for matching_option in matching_options:
            match_fuzziness = matching_option[1]
            match_frequency = original_strings[matching_option[0]]

            # we replace a name with a similar name only if the similar name
            # has a higher frequency; we also check that we only consider
            # reasonable matches, otherwise we might match with a fairly
            # different, but very prominent name
            matching_precision = match_fuzziness/100.0*match_frequency - original_frequency

            # finally, do the comparison by finding best match and checking that fuzziness is above some threshold
            if matching_precision > best_match_precision and match_fuzziness > threshold_fuzziness:
                best_match_precision = matching_precision
                best_match = matching_option[0]

            if debug:  # debug
                print matching_string + "[" + str(original_frequency) + "] vs.", matching_option, "-->", best_match, best_match_precision

        return best_match

    def find_best_match_tuple(self, matching_tuple, original_tuples,
                              threshold_fuzziness, matching_scaling_factor,
                              debug=None):
        """
        Finds the best match of a string tuple in an array of string tuples.

        Parameters
        ----------
        matching_tuple the tuple that is to be matched
        original_strings: the list of tuples from which the best match is to be found
        number_of_fuzzy_options: the number of alternatives of the matching_string fuzzywuzzy should find in the original_strings
        threshold_fuzziness: the lower threshold for the precision of fuzzy matches

        Returns
        -------
        String with the best match to matching_string in original_strings

        Note
        ----
        This method finds an element-wise best match for every element in the tuple
        and then constructs the overall best match.
        """
        best_distance = -10000000000.0  # a very large negative number so it is easy to beat by an entry in the original_tuples

        # the possible matches are the original_strings array reduced by the
        # string we are trying to match
        reduced_original_tuples = list(original_tuples)
        reduced_original_tuples.remove(matching_tuple)

        matching_frequency = original_tuples[matching_tuple]  # frequency of the matching tuple
        best_match = matching_tuple  # if we don't find any match, the original token is the best match

        matching_string = self.tuple_to_string(matching_tuple)  # construct a string from a token

        # loop over all remaining tuples and compute geometric distance
        for original_tuple in reduced_original_tuples:
            # make sure each entry has the same length as the matching_tuple
            if len(matching_tuple) != len(original_tuple):
                print "<< E: tuple length does not match: ", matching_tuple, original_tuple
                break

            # compute the frequency of the entire tuple (not the individual entries)
            entry_frequency = original_tuples[original_tuple]

            # go over each entry
            sum = 0.0  # the string distance between two tuples
            for i in range(0, len(original_tuple)):
                # compute the fuzz ratio of each entry
                entry_fuzz_ratio = fuzz.ratio(matching_tuple[i], original_tuple[i])
                # fuzzy ratio times entry frequency
                sum += (100 - entry_fuzz_ratio)*(100 - entry_fuzz_ratio)

            # the distance is computed as geometric distance of token distances, taking into account relative frequencies
            # the scaling factor determines the condition when to choose a worse-matching tuple that is much more
            # frequent
            distance = matching_scaling_factor*entry_frequency - matching_frequency*sqrt(sum)

            # to prevent always going with the most common tuple, we also compute the fuzzy distance between the string
            # versions of the tuples.
            original_string = self.tuple_to_string(original_tuple)
            fuzzy_distance = fuzz.ratio(matching_string, original_string)

            if distance > best_distance and fuzzy_distance > threshold_fuzziness:  # we have a new best match
                best_distance = distance
                best_match = original_tuple

            if debug:  # debug
                print matching_tuple, original_tuple, matching_frequency, entry_frequency, best_match, best_distance

        return [best_match, best_distance]

    def write_reduced_from_strings(self, out_file_name):
        """
        Write the reduced from string array to out_file

        Parameters:
        -----------
        out_file_name (str): the name of the output file
        """
        out_text = ""
        for key in self.reduced_from_strings.keys():
            out_text += key + ";" + str(self.reduced_from_strings[key]) + "\n"
        with open(out_file_name, 'w') as out_file:
            out_file.write(out_text)
