import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import cl from "../styles/ArticleItem.module.css";

const CATEGORY_MAPPING = {
    "Наука и образование": 1,
    "Энергетика": 2,
    "Просвещение и образование": 3,
    "Фотоэлектроника": 4,
    "Исследования в области медицины": 5,
    "Наука и технологии": 6,
    "Биология и сельское хозяйство": 7,
    "Нанотехнологии": 8,
    "Наука и туризм": 9,
    "Нейробиология": 10,
    "Климат и устойчивое развитие": 11,
    "Фотоника и телеком": 12,
    "Научно-популярные проекты": 13,
};

const ArticleItem = ({ searchQuery, selectedCategory, selectedSource }) => {
    const [posts, setPosts] = useState([]);
    const [filteredPosts, setFilteredPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchPosts = async () => {
            try {
                setLoading(true);
                const response = await fetch("http://109.73.202.54:8000/posts/");
                const data = await response.json();
                setPosts(data);
                setFilteredPosts(data);
            } catch (error) {
                console.error("Error fetching posts:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchPosts();
    }, []);

    useEffect(() => {
        let filtered = [...posts];

        // Поиск
        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            filtered = filtered.filter(post =>
                post.title.toLowerCase().includes(query) ||
                (post.content && post.content.toLowerCase().includes(query))
            );
        }

        // Категория
        if (
            selectedCategory &&
            selectedCategory !== "Категория" &&
            selectedCategory !== "Все"
        ) {
            const categoryId = CATEGORY_MAPPING[selectedCategory];
            filtered = filtered.filter(post => post.category === categoryId);
        }

        // Источник
        if (
            selectedSource &&
            selectedSource !== "Источник" &&
            selectedSource !== "Все"
        ) {
            filtered = filtered.filter(post => post.type === selectedSource);
        }

        setFilteredPosts(filtered);
    }, [searchQuery, selectedCategory, selectedSource, posts]);

    const handleReadMore = (postId) => {
        navigate(`/posts/${postId}`);
    };

    if (loading) {
        return <div className={cl.loading}>Загрузка...</div>;
    }

    if (filteredPosts.length === 0) {
        return <div className={cl.noResults}>Нет результатов по вашему запросу</div>;
    }

    return (
        <>
            {filteredPosts.map(post => (
                <div key={post.id} className={cl.card}>
                    <img
                        src='https://s3-alpha-sig.figma.com/img/4839/25f5/f5ce79046feb6f45b58ab338b1b00fd2?Expires=1744588800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=IKpgYQRa5TCsGMp68SlmTPJFBNpdeaa9CT4Gzu3AGIhW9RXALcw23sY5IFg-PrGMaADu-r9VZVw1zGv8F~~1iYJzbFgGMe2ejtWhUNvcoVb32Q8F80AGJDXHdpaIEvcyjsTJyZsPPT0RzZKZzTBOV9QQrhNanTqYS-VDp5DeJIAXaC7vjy9v4Gp9hmiUCTs0iSYcpnUbYvLTfgXagrVH~Q5Che60YCXf1ZRN5D1PSYWUJXTH05yr1T2g-vh4qunC-ieXtDUWu2YXIQXoac6kJz9LcEAYon0gRMv5ZW2sYKaiOKWv7cXzJanYfk~QC~HKWzTFFfZqsYMUeqzPF2-WVw__'
                        alt="Article"
                        className={cl.image}
                    />
                    <div className={cl.labels}>
                        <span className={cl.label}>{post.type}</span>
                        <span className={cl.label}>
                            {
                                Object.entries(CATEGORY_MAPPING).find(
                                    ([name, id]) => id === post.category
                                )?.[0] || "Неизвестно"
                            }
                        </span>
                    </div>
                    <h3 className={cl.title}>{post.title}</h3>
                    <button
                        onClick={() => handleReadMore(post.id)}
                        className={cl.readMore}
                    >
                        Читать
                    </button>
                </div>
            ))}
        </>
    );
};

export default ArticleItem;
