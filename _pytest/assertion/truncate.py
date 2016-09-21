""" Utilities for truncating assertion output """

import os

import py


DEFAULT_TRUNCATION_LENGTH = 8 * 80
TRUNCATION_USAGE_MSG = "use '-vv' to show"


def truncate_if_required(explanation, item, max_length=None):
    """
    Truncate this assertion explanation if the given test item is eligible.
    """
    if _should_truncate_item(item):
        return _truncate_explanation(explanation)
    return explanation


def _should_truncate_item(item):
    """
    Whether or not this test item is eligible for truncation.
    """
    verbose = item.config.option.verbose
    return verbose < 2 and not _running_on_ci()


def _truncate_explanation(input_lines, max_length=None):
    """
    Truncate given list of strings that makes up the assertion explanation.

    If the total length of the explanation is greater than max_length,
    it will be truncated at that point. The remaining lines will be replaced by
    a usage message.
    """
    if max_length is None:
        max_length = DEFAULT_TRUNCATION_LENGTH

    # Check if truncation required
    explanation_length = len("".join(input_lines))
    if explanation_length <= max_length:
        return input_lines

    # Find point at which input length exceeds total allowed length
    iterated_char_count = 0
    for iterated_index, input_line in enumerate(input_lines):
        if iterated_char_count + len(input_line) > max_length:
            break
        iterated_char_count += len(input_line)

    # Create truncated explanation with modified final line
    truncated_explanation = input_lines[:iterated_index]
    final_line = input_lines[iterated_index]
    if final_line:
        final_line_truncate_point = iterated_char_count - max_length
        final_line = final_line[:final_line_truncate_point] + "..."
    truncated_explanation.append(final_line)

    # Calculate count of truncated lines
    truncated_line_count = len(input_lines) - len(truncated_explanation)
    truncated_line_count += 1  # Account for the part-truncated final line

    # Append useful message to explanation
    msg = '...Full output truncated'
    if truncated_line_count == 1:
        msg += ' ({} line hidden)'.format(truncated_line_count)
    else:
        msg += ' ({} lines hidden)'.format(truncated_line_count)
    msg += ", {}" .format(TRUNCATION_USAGE_MSG)
    truncated_explanation.extend([
        py.builtin._totext(""),
        py.builtin._totext(msg),
    ])
    return truncated_explanation


def _running_on_ci():
    """Check if we're currently running on a CI system."""
    env_vars = ['CI', 'BUILD_NUMBER']
    return any(var in os.environ for var in env_vars)
