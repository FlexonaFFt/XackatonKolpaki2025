import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext()

export const useAuth = () => useContext(AuthContext)

export const AuthProvider = ({children}) => {
    const [isUserAuthenticated, setIsUserAuthenticated] = useState(false)
    const [isAdmin, setIsAdmin] = useState(false)

    useEffect(() => {
        const token = localStorage.getItem("token")
        if (token) {
            fetch("http://109.73.202.54:8000/users/me", {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.is_admin === true) {
                        setIsUserAuthenticated(true)
                        setIsAdmin(true)
                    } else {
                        setIsUserAuthenticated(true)
                        setIsAdmin(false)
                    }
                })
                .catch(() => {
                    setIsUserAuthenticated(false)
                    setIsAdmin(false)
                })
        }
    }, [])

    const setAuthenticationStatus = (status) => {
        setIsUserAuthenticated(status.isAuthenticated)
        setIsAdmin(status.isAdmin)
    }

    return (
        <AuthContext.Provider value={{isUserAuthenticated, isAdmin, setIsUserAuthenticated, setIsAdmin, setAuthenticationStatus}}>
            {children}
        </AuthContext.Provider>
    )
}