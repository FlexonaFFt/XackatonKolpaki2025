import React, { useState, useEffect } from "react";
import cl from '../styles/AdminPage.module.css';
import { useNavigate } from "react-router-dom";

const AdminPage = () => {
    const [pendingPosts, setPendingPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const navigate = useNavigate();
    
    const userData = JSON.parse(localStorage.getItem("userData"));
    const username = userData?.username;
    
    useEffect(() => {
        // Check if user is logged in
        if (!username) {
            navigate("/auth");
            return;
        }
        
        fetchPendingPosts();
    }, [username, navigate]);
    
    const fetchPendingPosts = async () => {
        try {
            console.log("Fetching pending posts...");
            const response = await fetch("http://109.73.202.54:8000/pending_posts/");
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log("Pending posts data:", data);
            
            setPendingPosts(data);
        } catch (error) {
            console.error("Error fetching pending posts:", error);
            setError("Ошибка при загрузке публикаций на модерацию: " + error.message);
        } finally {
            setLoading(false);
        }
    };
    
    const handleModerate = async (postId, approved) => {
        try {
            const response = await fetch(`http://109.73.202.54:8000/pending_posts/${postId}/moderate`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    admin_username: username,
                    approved
                }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log("Moderation response:", data);
            
            // Update the list after moderation
            setPendingPosts(pendingPosts.filter(post => post.id !== postId));
            alert(approved ? "Публикация одобрена" : "Публикация отклонена");
        } catch (error) {
            console.error("Error moderating post:", error);
            alert("Ошибка при модерации: " + error.message);
        }
    };
    
    if (loading) return <div className={cl.container}><div className={cl.loading}>Загрузка...</div></div>;

    return (
        <div className={cl.container}>
            <h1 className={cl.title}>Панель администратора</h1>
            <div className={cl.content}>
                <h2>Публикации на модерацию</h2>
                
                {error && <div className={cl.error}>{error}</div>}
                
                {pendingPosts.length === 0 ? (
                    <div className={cl.emptyMessage}>Нет публикаций на модерацию</div>
                ) : (
                    <div className={cl.postsList}>
                        {pendingPosts.map(post => (
                            <div key={post.id} className={cl.postCard}>
                                <h3 className={cl.postTitle}>{post.title}</h3>
                                <p className={cl.postAuthor}>Автор: {post.author_username}</p>
                                {post.created_at && (
                                    <p className={cl.postDate}>
                                        Дата: {new Date(post.created_at).toLocaleDateString()}
                                    </p>
                                )}
                                <div className={cl.postContent}>{post.content}</div>
                                
                                <div className={cl.moderationButtons}>
                                    <button
                                        className={`${cl.moderateButton} ${cl.approveButton}`}
                                        onClick={() => handleModerate(post.id, true)}
                                    >
                                        Одобрить
                                    </button>
                                    <button
                                        className={`${cl.moderateButton} ${cl.rejectButton}`}
                                        onClick={() => handleModerate(post.id, false)}
                                    >
                                        Отклонить
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminPage;