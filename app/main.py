import flet as ft
from commute_view import commute_view
from explore_view import explore_view
from favorites_view import favorites_view


def main(page: ft.Page):
    page.title = "NavigationRail Routing Example"

    routes = ["/explore", "/commute", "/favorites"]

    def get_content(route):
        if route == "/explore":
            return explore_view()
        elif route == "/commute":
            return commute_view()
        elif route == "/favorites":
            return favorites_view()
        else:
            return explore_view()

    def nav_change(e):
        page.go(routes[e.control.selected_index])

    def route_change(e):
        route = page.route if page.route in routes else "/explore"
        idx = routes.index(route)
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
                        get_content(route),
                        expand=True,
                        padding=20,
                    ),
                ],
                expand=True,
            )
        )

    page.on_route_change = route_change
    page.go(page.route or "/explore")


ft.app(target=main)
