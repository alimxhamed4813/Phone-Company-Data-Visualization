import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call

# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This class is not to be changed or instantiated. It is an Abstract Class.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ A new month has begun corresponding to <month> and <year>.
        This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        DO NOT CHANGE THIS METHOD
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """
   A contract for a phone line

    This class is not to be changed or instantiated. It is an Abstract Class.

    === Unique Public Attributes ===
    end:

    """
    # end date for TermContract obj
    end: datetime.date
    curr_date: datetime.date

    # Initialize new <start> and <end> times for TermContract
    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        super().__init__(start)
        self.end = end
        self.curr_date = start

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ A new month has begun corresponding to <month> and <year>.
        This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.curr_date = datetime.date(year, month, 1)
        self.bill = bill
        bill.set_rates("TERM", TERM_MINS_COST)
        bill.add_fixed_cost(TERM_MONTHLY_FEE)
        bill.add_free_minutes(0)
        if self.start.year == year and self.start.month == month:
            bill.add_fixed_cost(TERM_DEPOSIT)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        call_dur = ceil(call.duration / 60.0)  # call_dur turned to minutes
        if self.bill.free_min < TERM_MINS:

            if call_dur <= (TERM_MINS - self.bill.free_min):
                self.bill.add_free_minutes(call_dur)

            else:
                call_dur -= self.bill.free_min
                self.bill.add_free_minutes(TERM_MINS - self.bill.free_min)
                self.bill.add_billed_minutes(call_dur)
        else:
            self.bill.add_billed_minutes(call_dur)

        # self.bill.add_billed_minutes(call_dur)
        # if self.bill.free_min >= TERM_MINS:
        #     x = self.bill.free_min - TERM_MINS
        #     self.bill.add_billed_minutes(x)
        #     self.bill.free_min = 100

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None

        if self.curr_date > self.end:
            return self.bill.add_fixed_cost(-TERM_DEPOSIT)
        return self.bill.get_cost()


class MTMContract(Contract):
    """
    MTM Contracts
    """

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ A new month has begun corresponding to <month> and <year>.
        This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        bill.set_rates("MTM", MTM_MINS_COST)
        bill.add_fixed_cost(MTM_MONTHLY_FEE)


class PrepaidContract(Contract):
    """
    Prepaid Contracts
    """

    balance: float

    def __init__(self, start: datetime.date, balance: float,
                 ) -> None:
        super().__init__(start)
        self.balance = -balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ A new month has begun corresponding to <month> and <year>.
        This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        Prerequisite: When a new month is started, the balance from the
        previous month gets carried over into the new month, and if there is
        less than a $10 credit left in the account, the balance receives a
        top-up of $25 in credit (again, keep in mind that a negative amount
        indicates a credit). A top-up of $25 in credit means that the system
        adds 25 to the amount of credit available on the prepaid card. It
        does NOT mean that money is added until there is $25 of credit
        available.
        """
        if self.balance > -10:
            self.balance -= 25
        self.bill = bill
        bill.set_rates("PREPAID", PREPAID_MINS_COST)
        bill.add_fixed_cost(self.balance)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.balance += (ceil(call.duration / 60.0) * PREPAID_MINS_COST)
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.

        Note:
        - if the contract still has left some credit on it (a negative balance),
         then the amount left is forfeited
        """
        self.start = None
        if self.balance > 0:
            return self.bill.get_cost()
        return 0.0


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
