import { Component } from "react";
import { ADMIN_ROUTE, POSTS_ROUTE, AUTH_ROUTE, MAIN_PAGE_ROUTE, PUBLISH_ROUTE } from "./utils/consts";
import Auth from './pages/Auth'
import MainPage from "./pages/MainPage";
import PublishPage from './pages/PublishPage';
import AdminPage from "./pages/AdminPage";
import ArticlePage from "./pages/ArticlePage"

export const publicRoutes = [
    {
        path: AUTH_ROUTE,
        Component: Auth
    }
]

export const adminRoutes = [
    {
        path: ADMIN_ROUTE,
        Component: AdminPage
    }
]

export const privateRoutes = [
    {
        path: MAIN_PAGE_ROUTE,
        Component: MainPage
    },
    {
        path: PUBLISH_ROUTE,
        Component: PublishPage
    },
    {
        path: POSTS_ROUTE,
        Component: ArticlePage
    }
]