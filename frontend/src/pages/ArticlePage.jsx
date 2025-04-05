import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import cl from "../styles/ArticlePage.module.css";
import { AUTH_ROUTE } from "../utils/consts";
import Vector from "../UI/icons/Vector.png";

const ArticlePage = () => {
    const [post, setPost] = useState(null);
    const [recommendations, setRecommendations] = useState([]);
    const [liked, setLiked] = useState(false);
    const [telegramStatus, setTelegramStatus] = useState(null);
    const [telegramLoading, setTelegramLoading] = useState(false);
    const { post_id } = useParams();
    const navigate = useNavigate();

    const userData = JSON.parse(localStorage.getItem("userData"));
    const username = userData?.username;

    useEffect(() => {
        const fetchPost = async () => {
            try {
                const response = await fetch(`http://localhost:8000/posts/${post_id}`);
                if (!response.ok) throw new Error("Post not found");
                const data = await response.json();
                setPost(data);
            } catch (error) {
                console.error("Error fetching post:", error);
            }
        };

        const fetchRecommendations = async () => {
            if (!username) return;
            try {
                const response = await fetch(`http://localhost:8000/recommendations/${username}`);
                if (!response.ok) throw new Error("Failed to fetch recommendations");
                const data = await response.json();
                setRecommendations(data);
            } catch (error) {
                console.error("Error fetching recommendations:", error);
            }
        };

        const checkLiked = async () => {
            if (!username) return;
            try {
                const response = await fetch(`http://localhost:8000/users/${username}/likes`);
                const data = await response.json();
                if (Array.isArray(data)) {
                    const likedPostIds = data.map((like) => like.post_id);
                    setLiked(likedPostIds.includes(Number(post_id)));
                } else {
                    console.error("Ожидался массив, но получены данные:", data);
                }
            } catch (error) {
                console.error("Error checking liked posts:", error);
            }
        };
        
        // Add check for Telegram status
        const checkTelegramStatus = async () => {
            if (!username) return;
            try {
                const response = await fetch(`http://localhost:8000/users/${username}/telegram`);
                const data = await response.json();
                setTelegramStatus(data);
            } catch (error) {
                console.error("Error checking Telegram status:", error);
            }
        };
        
        fetchPost();
        fetchRecommendations();
        checkLiked();
        checkTelegramStatus();
    }, [post_id, username]);

    const handleLike = async () => {
        try {
            const response = await fetch(`http://localhost:8000/posts/${post_id}/like`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username }),
            });
    
            if (response.ok) {
                setLiked(true);
            } else {
                const err = await response.json();
                alert(err.detail || "Ошибка при лайке");
            }
        } catch (error) {
            console.error("Ошибка при лайке:", error);
            alert("Ошибка при подключении к серверу");
        }
    };

    const handleUnlike = async () => {
        try {
            const response = await fetch(`http://localhost:8000/posts/${post_id}/unlike`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username }),
            });

            if (response.ok) {
                setLiked(false);
            } else {
                const err = await response.json();
                alert(err.detail || "Ошибка при анлайке");
            }
        } catch (error) {
            console.error("Ошибка при анлайке:", error);
        }
    };

    const handleSendToTelegram = async () => {
        if (!username) {
            alert("Пожалуйста, войдите в аккаунт для отправки в Telegram");
            navigate(AUTH_ROUTE);
            return;
        }

        setTelegramLoading(true);
        try {
            // First check if user has Telegram connected
            const statusResponse = await fetch(`http://localhost:8000/users/${username}/telegram`);
            const statusData = await statusResponse.json();
            
            if (!statusData.is_linked) {
                // If not linked, show message with link
                alert(`${statusData.message}. Перейдите по ссылке: ${statusData.link}`);
                setTelegramStatus(statusData);
            } else {
                // If linked, send post
                const sendResponse = await fetch(
                    `http://localhost:8000/users/${username}/send_post/${post_id}`,
                    {
                        method: "POST",
                        headers: { "Content-Type": "application/json" }
                    }
                );
                
                const sendData = await sendResponse.json();
                
                if (sendData.success) {
                    alert("Сообщение отправлено в Telegram. Проверьте свой аккаунт.");
                } else {
                    alert(sendData.message);
                    if (sendData.link) {
                        alert(`Перейдите по ссылке для подключения: ${sendData.link}`);
                    }
                }
            }
        } catch (error) {
            console.error("Error sending to Telegram:", error);
            alert("Произошла ошибка при отправке в Telegram");
        } finally {
            setTelegramLoading(false);
        }
    };

    if (!post) return <div>Загрузка...</div>;

    return (
        <div className={cl.container}>
            <button onClick={() => navigate(-1)} className={cl.backButton}>← Назад</button>
            <div className={cl.meta}>
                <span className={cl.type}>{post.type}</span>
            </div>
            <img
                src="https://s3-alpha-sig.figma.com/img/4839/25f5/f5ce79046feb6f45b58ab338b1b00fd2?Expires=1744588800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=IKpgYQRa5TCsGMp68SlmTPJFBNpdeaa9CT4Gzu3AGIhW9RXALcw23sY5IFg-PrGMaADu-r9VZVw1zGv8F~~1iYJzbFgGMe2ejtWhUNvcoVb32Q8F80AGJDXHdpaIEvcyjsTJyZsPPT0RzZKZzTBOV9QQrhNanTqYS-VDp5DeJIAXaC7vjy9v4Gp9hmiUCTs0iSYcpnUbYvLTfgXagrVH~Q5Che60YCXf1ZRN5D1PSYWUJXTH05yr1T2g-vh4qunC-ieXtDUWu2YXIQXoac6kJz9LcEAYon0gRMv5ZW2sYKaiOKWv7cXzJanYfk~QC~HKWzTFFfZqsYMUeqzPF2-WVw__"
                alt="Article"
                className={cl.image}
            />
            <h1 className={cl.title}>{post.title}</h1>
            <div className={cl.content}>{post.author_us}</div>
            <div className={cl.content}>{post.content}</div>

            <div className={cl.likeButtonWrapper}>
                <button 
                    className={cl.publishBtn}
                    onClick={handleSendToTelegram}
                    disabled={telegramLoading}
                >
                    {telegramLoading ? "Отправка..." : "Отправить в Telegram"}
                </button>
                <div className={cl.obv}>
                    <img
                        src={Vector}
                        alt="like"
                        onClick={liked ? handleUnlike : handleLike}
                        className={liked ? cl.likedIcon : cl.likeIcon}
                    />
                </div>
            </div>

            // In the recommendations section
            <div className={cl.recommendations}>
                <h1 className={cl.title}>Рекомендованные публикации</h1>
                {recommendations.length > 0 ? (
                    <div className={cl.recommendationWrapper}>
                        {recommendations.map((rec) => (
                            <div
                                key={rec.post_id}
                                className={cl.recommendationItem}
                                onClick={() => navigate(`/posts/${rec.post_id}`)}
                            >
                                <img
                                    src='https://s3-alpha-sig.figma.com/img/4839/25f5/f5ce79046feb6f45b58ab338b1b00fd2?Expires=1744588800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=IKpgYQRa5TCsGMp68SlmTPJFBNpdeaa9CT4Gzu3AGIhW9RXALcw23sY5IFg-PrGMaADu-r9VZVw1zGv8F~~1iYJzbFgGMe2ejtWhUNvcoVb32Q8F80AGJDXHdpaIEvcyjsTJyZsPPT0RzZKZzTBOV9QQrhNanTqYS-VDp5DeJIAXaC7vjy9v4Gp9hmiUCTs0iSYcpnUbYvLTfgXagrVH~Q5Che60YCXf1ZRN5D1PSYWUJXTH05yr1T2g-vh4qunC-ieXtDUWu2YXIQXoac6kJz9LcEAYon0gRMv5ZW2sYKaiOKWv7cXzJanYfk~QC~HKWzTFFfZqsYMUeqzPF2-WVw__'
                                    alt="Article"
                                    className={cl.image}
                                />
                                <p className={cl.recText}>{rec.title}</p>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className={cl.recommendations}>
                        <h2>Рекомендации отсутствуют</h2>
                    </div>
                )}
            </div>

        </div>
    );
};

export default ArticlePage;
