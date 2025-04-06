import React, { useState, useEffect } from "react";
import cl from "../styles/Auth.module.css";
import {useNavigate} from 'react-router-dom'
import { MAIN_PAGE_ROUTE } from '../utils/consts'
import { useAuth } from "../context/AuthContext";

const API_URL = "http://109.73.202.54:8000";

const Auth = () => {
    const [isLogin, setIsLogin] = useState(true)
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [userRole, setUserRole] = useState("user") // Добавляем роль пользователя
    const [userData, setUserData] = useState(JSON.parse(localStorage.getItem("userData") || "null"))
    const {setAuthenticationStatus} = useAuth()
    const navigate = useNavigate()

    useEffect(() => {
        if (userData) {
            // Если у нас есть данные пользователя, считаем его авторизованным
            setAuthenticationStatus({
                isAuthenticated: true,
                isAdmin: userData.who_is_user === "admin",
            })
        }
    }, [userData, setAuthenticationStatus])

    const handleAuth = async (e) => {
        e.preventDefault()
        const endpoint = isLogin ? "/login" : "/users/";
        const payload = isLogin
            ? {username, password}
            : {username, password, who_is_user: userRole}

        try {
            const response = await fetch(`${API_URL}${endpoint}`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload),
            })

            const data = await response.json()
            if (response.ok) {
                if (isLogin) {
                    // Сохраняем данные пользователя в localStorage
                    localStorage.setItem("userData", JSON.stringify(data))
                    setUserData(data)
                    setAuthenticationStatus({
                        isAuthenticated: true,
                        isAdmin: data.who_is_user === "admin",
                    })
                    navigate(MAIN_PAGE_ROUTE)
                } else {
                    alert("Регистрация успешна! Теперь войдите.")
                    setIsLogin(true)
                }
            } else {
                alert(data.detail || "Ошибка авторизации/регистрации")
            }
        } catch (error) {
            console.error("Ошибка при авторизации:", error)
            alert("Произошла ошибка при подключении к серверу")
        }
    }

    const logout = () => {
        localStorage.removeItem("userData")
        setUserData(null)
        setUsername("")
        setPassword("")
        setAuthenticationStatus({isAuthenticated: false, isAdmin: false})
    }

    return (
        <div className={cl.authContainer}>
            {userData ? (
                <div className={cl.loggedIn}>
                    <p>Вы авторизованы как <strong>{userData.username}</strong></p>
                    <p>Роль: {userData.who_is_user}</p>
                    <button className={cl.loginButton} onClick={() => navigate(MAIN_PAGE_ROUTE)}>Продолжить</button>
                    <button className={cl.logoutButton} onClick={logout}>Выйти</button>
                </div>
            ) : (
                <form onSubmit={handleAuth} className={cl.authForm}>
                    <h2>{isLogin ? "Вход" : "Регистрация"}</h2>
                    <input
                        type="text"
                        placeholder="Логин"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                        className={cl.inputField}
                    />
                    <input
                        type="password"
                        placeholder="Пароль"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        className={cl.inputField}
                    />
                    
                    {!isLogin && (
                        <select 
                            value={userRole} 
                            onChange={(e) => setUserRole(e.target.value)}
                            className={cl.inputField}
                        >
                            <option value="user">Пользователь</option>
                            <option value="redactor">Редактор</option>
                            <option value="admin">Администратор</option>
                        </select>
                    )}
                    
                    <button type="submit" className={cl.authButton}>
                        {isLogin ? "Войти" : "Зарегистрироваться"}
                    </button>
                    <p className={cl.switchText} onClick={() => setIsLogin(!isLogin)}>
                        {isLogin ? "Нет аккаунта? Зарегистрируйтесь" : "Уже есть аккаунт? Войти"}
                    </p>
                </form>
            )}
        </div>
    )
}

export default Auth