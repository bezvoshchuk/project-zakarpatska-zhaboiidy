from __future__ import annotations

from collections import UserDict
import warnings

from datamodels.fields import Name, Hobby, ProjectRole, ProjectTasks


class Note:
    """This class initialises new Note with the name and project role"""

    def __init__(
        self,
        name_: str,
        project_role: str,
        project_tasks: str = None,
        hobbies: list[str] = None,
    ):
        self.name: Name = Name(name_)
        self.project_role: ProjectRole = ProjectRole(project_role)
        self.project_tasks: ProjectTasks = ProjectTasks(project_tasks)
        self.hobbies: list[Hobby] = [Hobby(hobby) for hobby in (hobbies or [])]

    def add_project_role(self, project_role: str):
        """Add project role to note"""
        self.project_role = ProjectRole(project_role)

    def add_project_tasks(self, project_tasks: str):
        """Add project tasks to note"""
        self.project_tasks = ProjectTasks(project_tasks)

    def add_hobby(self, hobby: str):
        """Add hobby to note if not already present.

        Args:
            hobby: Hobby to add.
        """
        try:
            self.find_hobby(hobby)
            warnings.warn(
                f"Hobby {hobby} was already added to note for {self.name}, skipping ..."
            )
        except KeyError:
            self.hobbies.append(Hobby(hobby))

    def find_hobby(self, hobby: str):
        """Find hobby record by value.

        Args:
            hobby: Hobby to find.

        Raises:
            KeyError: if hobby does not exist.

        Returns:
            A Hobby object that is identical to the one being looked up.
        """
        for _hobby in self.hobbies:

            if _hobby.value.casefold() == hobby.casefold():
                return _hobby
        else:
            raise KeyError(
                f"Hobby {hobby} is not mentionned in the note for {self.name}"
            )

    def remove_hobby(self, hobby: str):
        """Remove hobby from note.

        Args:
            hobby: Hobby to add.

        Raises:
            KeyError: if hobby does not exist.
        """
        _hobby = self.find_hobby(hobby)
        self.hobbies.remove(_hobby)

    def edit_hobby(self, hobby: str, new_hobby: str):
        """Edit hobby.

        Args:
            hobby: Hobby value to edit.
            new_hobby: Hobby value to change to.

        Raises:
            KeyError: if hobby does not exist.
        """

        self.remove_hobby(hobby)
        self.add_hobby(new_hobby)

    def __str__(self):
        return (
            f"\n\tNote for: {self.name.value}"
            f"\n\tproject role: {self.project_role}"
            f"\n\tproject tasks: {self.project_tasks}"
            f"\n\thobbies: {'; '.join(h.value for h in self.hobbies)}"
        )


class NotesBook(UserDict):
    """Class that gathers all notes into one dict with the names of notes as keys and Note classes as values"""

    data: dict[str, Note] = {}

    def print_notes_book(self):
        """Print all notes"""

        for name, note in self.data.items():
            print(note)

    def load_data_from_json(self, json_data):
        """Print all existing notes from file"""

        self.data = {
            _note_data["name_"]: Note(**_note_data) for _note_data in json_data
        }

    def dump_data_to_json(self):
        """Save notes to file"""

        return [
            {
                "name_": _note.name.value,
                "project_role": str(_note.project_role),
                "project_tasks": str(_note.project_tasks),
                "hobbies": [hobby.value for hobby in _note.hobbies],
            }
            for _note in self.data.values()
        ]

    def add_note(self, note_: Note) -> Note | None:
        """Add a note to notes book if not already present.

        Args:
            note_: Note to add.
        """
        if note_.name.value not in self.data:
            self.data[note_.name.value] = note_
            return note_

    def find(self, name_: str) -> Note:
        """Find a note in the notes book by name.

        Args:
            name_: Username of the user to find.

        Raises:
            KeyError: if note doesn't exist.
        """
        if name_ not in self.data:
            raise KeyError(f"Note for {name_} was not found.")

        return self.data[name_]

    def find_project_role(self, project_role_: str) -> list[Note]:
        """Find a note/s in the notes book by project role.

        Args:
            project_role_: Project role of to find.

        Raises:
            KeyError: if note doesn't exist.
        """

        notes = list(
            filter(
                lambda note_: note_.project_role.value == project_role_,
                self.data.values(),
            )
        )

        if not notes:
            raise KeyError(f"Note for {project_role_} was not found.")

        return notes

    def find_hobby(self, hobby_: str) -> list[Note]:
        """Find a notes in the notes book by hobby.

        Args:
            hobby_: Hobby role of to find.

        Raises:
            KeyError: if note doesn't exist.
        """
        notes = list(
            filter(
                lambda note_: any(
                    _hobby.value.casefold() == hobby_.casefold()
                    for _hobby in note_.hobbies
                ),
                self.data.values(),
            )
        )

        if not notes:
            raise KeyError(f"Notes with {hobby_} were not found.")

        return notes

    def delete(self, name_: str) -> None:
        """Delete a note in the notes book by name.

        Args:
            name_: Name of the note to find.

        Raises:
            KeyError: if record doesn't exist.
        """

        del self.data[name_]
