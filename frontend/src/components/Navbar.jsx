import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import cl from "../styles/Navbar.module.css";
import { ADMIN_ROUTE, AUTH_ROUTE, PUBLISH_ROUTE, MAIN_PAGE_ROUTE } from "../utils/consts";

const Navbar = () => {
    const navigate = useNavigate();
    const {isAdmin, isUserAuthenticated, setAuthenticationStatus} = useAuth()

    const handleLogout = () => {
        localStorage.removeItem("userData")
        setAuthenticationStatus({isAuthenticated: false, isAdmin: false})
        navigate(AUTH_ROUTE)
    }

    return (
        <nav className={cl.navbar}>
            <div className={cl.logo} onClick={() => navigate(MAIN_PAGE_ROUTE)}>Logo</div>
            <div className={cl.buttons}>
                {isAdmin && isUserAuthenticated && (
                    <button className={cl.profileBtn} onClick={() => navigate(ADMIN_ROUTE)}>Панель администратора</button>
                )}
                {isUserAuthenticated ? (
                    <>
                        <button className={cl.profileBtn} onClick={() => navigate(MAIN_PAGE_ROUTE)}>Новости</button>
                        <button className={cl.publishBtn} onClick={() => navigate(PUBLISH_ROUTE)}>Опубликовать пост</button>
                        <button className={cl.profileBtn} onClick={handleLogout}>Выйти</button>
                    </>
                ) : (
                    <button className={cl.publishBtn} onClick={() => navigate(AUTH_ROUTE)}>Войти в аккаунт</button>
                )}
            </div>
        </nav>
    )
}

export default Navbar