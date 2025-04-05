import React, { useState } from "react";
import cl from "../styles/PublishPage.module.css";
import { useNavigate } from "react-router-dom";

const PublishPage = () => {
    const [title, setTitle] = useState("");
    const [text, setText] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const navigate = useNavigate();

    // Получаем данные пользователя из localStorage
    const userData = JSON.parse(localStorage.getItem("userData"));
    const username = userData?.username;

    const handleSubmit = async (e) => {
        e.preventDefault();
    
        if (!username) {
            setError("Необходимо войти в систему");
            return;
        }
        
        const postData = {
            title,
            content: text,
            username,
        };
    
        setLoading(true);
        setError(null);
    
        try {
            console.log("Отправка данных на модерацию:", postData);
            
            // Use the pending_posts endpoint instead of posts
            const response = await fetch("http://localhost:8000/pending_posts/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(postData),
            });
    
            console.log("Статус ответа:", response.status);
            
            const responseData = await response.json();
            console.log("Ответ сервера:", responseData);
            
            if (!response.ok) {
                throw new Error(responseData.detail || "Ошибка при отправке на модерацию");
            }
    
            setSuccess(true);
            setTitle("");
            setText("");
        } catch (error) {
            console.error("Ошибка при отправке данных:", error);
            setError(error.message || "Произошла неизвестная ошибка");
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className={cl.container}>
            <h1 className={cl.title}>Ваша публикация</h1>
            <form className={cl.form} onSubmit={handleSubmit}>
                <label className={cl.label}>ЗАГОЛОВОК - ДО 50 СИМВОЛОВ</label>
                <input
                    type="text"
                    className={cl.input}
                    placeholder="Введите заголовок поста"
                    maxLength={50}
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                />
                <label className={cl.label}>ТЕКСТ</label>
                <textarea
                    className={cl.textarea}
                    placeholder="Введите текст поста"
                    value={text}
                    onChange={(e) => {
                        setText(e.target.value);
                        e.target.style.height = "auto";
                        e.target.style.height = `${e.target.scrollHeight}px`;
                    }}
                    required
                    rows={1}
                />
                <button type="submit" className={cl.button} disabled={loading}>
                    {loading ? "Отправляется..." : "Отправить на модерацию"}
                </button>
            </form>

            {success && <p className={cl.successMessage}>Публикация успешно отправлена на модерацию!</p>}
            {error && <p className={cl.errorMessage}>Ошибка: {error}</p>}
        </div>
    );
};

export default PublishPage;
