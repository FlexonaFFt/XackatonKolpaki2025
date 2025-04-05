import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import cl from "../styles/Navbar.module.css";
import { ADMIN_ROUTE, AUTH_ROUTE, PUBLISH_ROUTE, MAIN_PAGE_ROUTE } from "../utils/consts";
import kolpaknews from '../UI/icons/kolpaknews.svg';

const Navbar = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false); // Состояние для открытия меню
    const navigate = useNavigate();
    const { isAdmin, isUserAuthenticated, setAuthenticationStatus } = useAuth();

    const handleLogout = () => {
        localStorage.removeItem("userData");
        setAuthenticationStatus({ isAuthenticated: false, isAdmin: false });
        navigate(AUTH_ROUTE);
        setIsMenuOpen(false); // Закрыть меню при выходе
    };

    const handleMenuItemClick = () => {
        setIsMenuOpen(false); // Закрыть меню при клике на элемент
    };

    return (
        <nav className={cl.navbar}>
            <div className={cl.logo} onClick={() => navigate(MAIN_PAGE_ROUTE)}>
                <img src={kolpaknews} alt="Logo" className={cl.logo} />
            </div>

            {/* Скрытое меню для мобильных устройств */}
            <div className={`${cl.buttons} ${isMenuOpen ? cl.open : ''}`}>
                {isAdmin && isUserAuthenticated && (
                    <button className={cl.profileBtn} onClick={() => { navigate(ADMIN_ROUTE); handleMenuItemClick(); }}>Панель администратора</button>
                )}
                {isUserAuthenticated ? (
                    <>
                        <button className={cl.profileBtn} onClick={() => { navigate(MAIN_PAGE_ROUTE); handleMenuItemClick(); }}>Новости</button>
                        <button className={cl.publishBtn} onClick={() => { navigate(PUBLISH_ROUTE); handleMenuItemClick(); }}>Опубликовать пост</button>
                        <button className={cl.profileBtn} onClick={handleLogout}>Выйти</button>
                    </>
                ) : (
                    <button className={cl.publishBtn} onClick={() => { navigate(AUTH_ROUTE); handleMenuItemClick(); }}>Войти в аккаунт</button>
                )}
            </div>

            {/* Кнопка для открытия меню на мобильных устройствах */}
            <div className={cl.menuToggle} onClick={() => setIsMenuOpen(!isMenuOpen)}>
                ☰
            </div>
        </nav>
    );
};

export default Navbar;
