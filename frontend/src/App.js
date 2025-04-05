import React from "react";
import AppRouter from './components/AppRouter'
import { BrowserRouter } from "react-router-dom";
import Footer from "./components/Footer";
import { AuthProvider } from "./context/AuthContext";
import Navbar from './components/Navbar'

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Navbar />
                <AppRouter />
                <Footer />
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App