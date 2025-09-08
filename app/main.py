import flet as ft
from commute_view import commute_view
from explore_view import explore_view
from favorites_view import favorites_view


def main(page: ft.Page):
    page.title = "NavigationRail Example"
    selected_index = 0

    def get_content(idx):
        if idx == 0:
            return explore_view()
        elif idx == 1:
            return commute_view()
        elif idx == 2:
            return favorites_view()
        else:
            return explore_view()

    def nav_change(e):
        idx = e.control.selected_index
        page.clean()
        page.add(
            ft.Row(
                [
                    ft.NavigationRail(
                        selected_index=idx,
                        destinations=[
                            ft.NavigationRailDestination(
                                icon=ft.Icons.EXPLORE, label="Explore"
                            ),
                            ft.NavigationRailDestination(
                                icon=ft.Icons.COMMUTE, label="Commute"
                            ),
                            ft.NavigationRailDestination(
                                icon=ft.Icons.BOOKMARK_BORDER,
                                selected_icon=ft.Icons.BOOKMARK,
                                label="Favorites",
                            ),
                        ],
                        on_change=nav_change,
                    ),
                    ft.Container(
                        get_content(idx),
                        expand=True,
                        padding=20,
                    ),
                ],
                expand=True,
            )
        )

    # Initial render
    class DummyEvent:
        def __init__(self, idx):
            self.control = type("obj", (object,), {"selected_index": idx})

    nav_change(DummyEvent(selected_index))


ft.app(target=main)
