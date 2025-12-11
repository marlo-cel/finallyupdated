from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class TicketPriority(Enum):
    """Enum for ticket priority levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

    @classmethod
    def values(cls) -> List[str]:
        return [p.value for p in cls]


class TicketStatus(Enum):
    """Enum for ticket status."""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    WAITING_FOR_USER = "Waiting for User"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

    @classmethod
    def values(cls) -> List[str]:
        return [s.value for s in cls]


class ITTicket:
    """
    Represents an IT support ticket.

    Think of this as a help desk ticket - when something breaks or needs
    fixing, you create one of these to track the problem and its solution.

    Attributes:
        ticket_id: Unique identifier
        description: What's the problem
        priority: How urgent (Low, Medium, High, Critical)
        status: Current state (Open, Resolved, etc.)
        assigned_to: Who's working on it
        created_at: When ticket was created
        resolution_time_hours: How long it took to resolve
        opened_by: User ID who created ticket
    """

    # Service Level Agreement (SLA) times in hours
    SLA_TIMES = {
        TicketPriority.CRITICAL.value: 4,
        TicketPriority.HIGH.value: 24,
        TicketPriority.MEDIUM.value: 48,
        TicketPriority.LOW.value: 72
    }

    def __init__(self,
                 ticket_id: Optional[int],
                 description: str,
                 priority: str = "Medium",
                 status: str = "Open",
                 assigned_to: Optional[str] = None,
                 created_at: Optional[datetime] = None,
                 resolution_time_hours: Optional[float] = None,
                 opened_by: Optional[int] = None):
        """
        Initialize an ITTicket.

        Args:
            ticket_id: Unique ID (None for new tickets)
            description: Problem description
            priority: Ticket priority
            status: Current status
            assigned_to: Assigned support person
            created_at: When created (auto-set if None)
            resolution_time_hours: Time to resolve
            opened_by: User ID who opened ticket
        """
        self.ticket_id = ticket_id
        self.description = description
        self.priority = priority
        self.status = status
        self.assigned_to = assigned_to
        self.created_at = created_at or datetime.now()
        self.resolution_time_hours = resolution_time_hours
        self.opened_by = opened_by

        # Validate
        self._validate()

    def _validate(self) -> None:
        """
        Validate ticket attributes.

        Raises:
            ValueError: If validation fails
        """
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")

        if self.priority not in TicketPriority.values():
            raise ValueError(f"Invalid priority. Must be one of: {TicketPriority.values()}")

        if self.status not in TicketStatus.values():
            raise ValueError(f"Invalid status. Must be one of: {TicketStatus.values()}")

        if self.resolution_time_hours is not None and self.resolution_time_hours < 0:
            raise ValueError("Resolution time cannot be negative")

    @classmethod
    def create_from_csv_row(cls, row: Dict[str, Any]) -> 'ITTicket':
        """
        Factory method to create ITTicket from CSV data.

        Args:
            row: Dictionary with CSV row data

        Returns:
            New ITTicket object
        """
        created_at = None
        if row.get('created_at'):
            try:
                created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                created_at = datetime.now()

        resolution_time = None
        if row.get('resolution_time_hours'):
            try:
                resolution_time = float(row['resolution_time_hours'])
            except (ValueError, TypeError):
                resolution_time = None

        return cls(
            ticket_id=int(row['ticket_id']) if row.get('ticket_id') else None,
            description=row.get('description', 'No description'),
            priority=row.get('priority', 'Medium'),
            status=row.get('status', 'Open'),
            assigned_to=row.get('assigned_to'),
            created_at=created_at,
            resolution_time_hours=resolution_time,
            opened_by=None
        )

    def assign_to(self, support_person: str) -> None:
        """
        Assign ticket to a support person.

        Args:
            support_person: Name of support person
        """
        self.assigned_to = support_person
        if self.status == TicketStatus.OPEN.value:
            self.status = TicketStatus.IN_PROGRESS.value

    def resolve(self, resolution_hours: float) -> None:
        """
        Mark ticket as resolved.

        Args:
            resolution_hours: How long it took to resolve
        """
        if resolution_hours < 0:
            raise ValueError("Resolution time cannot be negative")

        self.status = TicketStatus.RESOLVED.value
        self.resolution_time_hours = resolution_hours

    def is_open(self) -> bool:
        """Check if ticket is still open."""
        return self.status in [
            TicketStatus.OPEN.value,
            TicketStatus.IN_PROGRESS.value,
            TicketStatus.WAITING_FOR_USER.value
        ]

    def is_resolved(self) -> bool:
        """Check if ticket is resolved or closed."""
        return self.status in [TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value]

    def get_age_hours(self) -> float:
        """
        Calculate how many hours since ticket was created.

        Returns:
            Number of hours
        """
        time_diff = datetime.now() - self.created_at
        return round(time_diff.total_seconds() / 3600, 1)

    def get_sla_deadline_hours(self) -> int:
        """
        Get SLA deadline in hours based on priority.

        Returns:
            SLA hours
        """
        return self.SLA_TIMES.get(self.priority, 48)

    def is_sla_breached(self) -> bool:
        """
        Check if ticket has breached SLA.

        Returns:
            True if SLA breached (still open past deadline)
        """
        if not self.is_open():
            return False

        age_hours = self.get_age_hours()
        sla_hours = self.get_sla_deadline_hours()

        return age_hours > sla_hours

    def get_priority_weight(self) -> int:
        """
        Get numeric weight for priority (for sorting).

        Returns:
            Priority weight (0=Critical, 3=Low)
        """
        weights = {
            TicketPriority.CRITICAL.value: 0,
            TicketPriority.HIGH.value: 1,
            TicketPriority.MEDIUM.value: 2,
            TicketPriority.LOW.value: 3
        }
        return weights.get(self.priority, 2)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ticket to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'ticket_id': self.ticket_id,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolution_time_hours': self.resolution_time_hours,
            'opened_by': self.opened_by
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ITTicket':
        """
        Create ITTicket from dictionary.

        Args:
            data: Dictionary with ticket data

        Returns:
            ITTicket object
        """
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])

        return cls(
            ticket_id=data.get('ticket_id'),
            description=data['description'],
            priority=data.get('priority', 'Medium'),
            status=data.get('status', 'Open'),
            assigned_to=data.get('assigned_to'),
            created_at=created_at,
            resolution_time_hours=data.get('resolution_time_hours'),
            opened_by=data.get('opened_by')
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"ITTicket(id={self.ticket_id}, priority='{self.priority}', "
                f"status='{self.status}')")

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"[{self.priority}] {self.description[:50]}... - {self.status}"

    def __eq__(self, other) -> bool:
        """Check equality based on ticket_id."""
        if not isinstance(other, ITTicket):
            return False
        return self.ticket_id == other.ticket_id

    def __lt__(self, other) -> bool:
        """
        Compare tickets for sorting (by priority, then age).
        Higher priority and older tickets come first.
        """
        if not isinstance(other, ITTicket):
            return NotImplemented

        # Compare by priority first
        if self.priority != other.priority:
            return self.get_priority_weight() < other.get_priority_weight()

        # If same priority, older tickets first
        return self.created_at < other.created_at