from dataclasses import dataclass


@dataclass
class User:
    id: str
    email: str
    full_name: str = ""


@dataclass
class Course:
    id: str
    title: str
    status: str = ""


@dataclass
class Notification:
    id: str
    title: str
    read: bool = False
