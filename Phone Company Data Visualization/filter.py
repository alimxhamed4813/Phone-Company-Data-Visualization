import time
import datetime
from call import Call
from customer import Customer


class Filter:
    """ A class for filtering customer data on some criterion. A filter is
    applied to a set of calls.

    This is an abstract class. Only subclasses should be instantiated.
    """

    def __init__(self) -> None:
        pass

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all calls from <data>, which match the filter
        specified in <filter_string>.

        The <filter_string> is provided by the user through the visual prompt,
        after selecting this filter.
        The <customers> is a list of all customers from the input dataset.

         If the filter has
        no effect or the <filter_string> is invalid then return the same calls
        from the <data> input.

        Note that the order of the output matters, and the output of a filter
        should have calls ordered in the same manner as they were given, except
        for calls which have been removed.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        - all calls included in <data> are valid calls from the input dataset
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        raise NotImplementedError


class ResetFilter(Filter):
    """
    A class for resetting all previously applied filters, if any.
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Reset all of the applied filters. Return a List containing all the
        calls corresponding to <customers>.
        The <data> and <filter_string> arguments for this type of filter are
        ignored.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        """
        filtered_calls = []
        for c in customers:
            customer_history = c.get_history()
            # only take outgoing calls, we don't want to include calls twice
            filtered_calls.extend(customer_history[0])
        return filtered_calls

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Reset all of the filters applied so far, if any"


class CustomerFilter(Filter):
    """
    A class for selecting only the calls from a given customer.
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data> made or
        received by the customer with the id specified in <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains a valid
        customer ID.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """
        try:
            filtered_lst = []
            curr_customer = None
            if not filter_string.isnumeric() or len(filter_string) != 4:
                return data

            for customer in customers:
                if customer.get_id() == int(filter_string):
                    curr_customer = customer

            for call in data:
                if call.src_number in curr_customer.get_phone_numbers():
                    filtered_lst.append(call)
            return filtered_lst

        except (TypeError, ValueError, AttributeError):
            return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter events based on customer ID"


class DurationFilter(Filter):
    """
    A class for selecting only the calls lasting either over or under a
    specified duration.
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data> with a duration
        of under or over the time indicated in the <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains the following
        input format: either "Lxxx" or "Gxxx", indicating to filter calls less
        than xxx or greater than xxx seconds, respectively.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!

        """
        try:
            if (filter_string[0] != 'G' and filter_string[0] != 'L') and (
                    not filter_string[1:].isnumeric()):
                return data

            if len(filter_string) != 4:
                return data

            durr_lst = []

            if filter_string[0] == 'G':
                for durr in data:
                    if durr.duration > int(filter_string[1:]):
                        durr_lst.append(durr)

            if filter_string[0] == 'L':
                for durr in data:
                    if durr.duration < int(filter_string[1:]):
                        durr_lst.append(durr)
            return durr_lst

        except (TypeError, ValueError, AttributeError, IndexError):
            return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls based on duration; " \
               "L### returns calls less than specified length, G### for greater"


class LocationFilter(Filter):
    """
    A class for selecting only the calls that took place within a specific area
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data>, which took
        place within a location specified by the <filter_string>
        (at least the source or the destination of the event was
        in the range of coordinates from the <filter_string>).

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains four valid
        coordinates within the map boundaries.
        These coordinates represent the location of the lower left corner
        and the upper right corner of the search location rectangle,
        as 2 pairs of longitude/latitude coordinates, each separated by
        a comma and a space:
          lowerLong, lowerLat, upperLong, upperLat
        Calls that fall exactly on the boundary of this rectangle are
        considered a match as well.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!

        Toronto map coordinates:
          Lower-left corner: -79.697878 (long), 43.576959 (lat)
          Upper-right corner: -79.196382 (long), 43.799568 (lat)
        """
        try:
            coordinates = filter_string.split(",")
            lower_long = float(coordinates[0])
            lower_lat = float(coordinates[1])
            upper_long = float(coordinates[2])
            upper_lat = float(coordinates[3])

            if lower_lat > upper_lat:
                return data
            if lower_long > upper_long:
                return data

            if lower_long < -79.697878:
                return data
            if lower_lat < 43.576959:
                return data
            if upper_long > 79.196382:
                return data
            if upper_lat > 43.799568:
                return data

            # append qualifying outgoing calls
            lst = []
            for call in data:
                long = call.src_loc[0]
                lat = call.src_loc[1]

                if (upper_long >= long >= lower_long) and (
                        upper_lat >= lat >= lower_lat):
                    lst.append(call)

            # append qualifying incoming calls
            for call in data:
                long = call.dst_loc[0]
                lat = call.dst_loc[1]

                if (upper_long >= long >= lower_long) and (
                        upper_lat >= lat >= lower_lat):
                    lst.append(call)

            return lst
        except (TypeError, ValueError, AttributeError):
            return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls made or received in a given rectangular area. " \
               "Format: \"lowerLong, lowerLat, " \
               "upperLong, upperLat\" (e.g., -79.6, 43.6, -79.3, 43.7)"


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'time', 'datetime', 'call', 'customer'
        ],
        'max-nested-blocks': 4,
        'allowed-io': ['apply', '__str__'],
        'disable': ['W0611', 'W0703'],
        'generated-members': 'pygame.*'
    })
