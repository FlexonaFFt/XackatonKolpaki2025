import React, { useState, useEffect, useRef } from "react";
import ArticleItem from "../components/ArticleItem";
import cl from "../styles/MainPage.module.css";
import searchIcon from "../UI/icons/search.png";
import { useNavigate } from "react-router-dom"; 
import axios from 'axios'

const MainPage = () => {
    const [openMenu, setOpenMenu] = useState(null);
    const [selectedCategory, setSelectedCategory] = useState("Категория");
    const [selectedSource, setSelectedSource] = useState("Источник");
    const [searchQuery, setSearchQuery] = useState(""); 
    const [recommendations, setRecommendations] = useState([]); 

    const userData = JSON.parse(localStorage.getItem("userData"));
    const username = userData?.username;

    const menuRef = useRef(null);
    const navigate = useNavigate(); 

    const [categories, setCategories] = useState([]);

    useEffect(() => {
        axios.get("http://109.73.202.54:8000/categories/")
            .then(res => {
                setCategories(["Все", ...res.data]);
            })
            .catch(err => {
                console.error("Ошибка загрузки категорий:", err);
            });
    }, []);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (menuRef.current && !menuRef.current.contains(event.target)) {
                setOpenMenu(null);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    useEffect(() => {
        const fetchRecommendations = async () => {
            try {
                const response = await fetch(`http://109.73.202.54:8000/recommendations/${username}`); // Эндпоинт для получения рекомендаций
                if (!response.ok) throw new Error("Failed to fetch recommendations");
                const data = await response.json();
                setRecommendations(data);
            } catch (error) {
                console.error("Error fetching recommendations:", error);
            }
        };

        fetchRecommendations();
    }, []);

    const toggleMenu = (menu) => {
        setOpenMenu(openMenu === menu ? null : menu);
    };

    const selectCategory = (category) => {
        setSelectedCategory(category);
        setOpenMenu(null);
    };

    const selectSource = (source) => {
        setSelectedSource(source);
        setOpenMenu(null);
    };

    const handleSearchChange = (e) => {
        setSearchQuery(e.target.value);
    };

    return (
        <div className={cl.container} ref={menuRef}>
            <h1 className={cl.title}>Главная</h1>

            <div className={cl.searchWrapper}>
                <img src={searchIcon} alt="Search" className={cl.searchIcon} />
                <input
                    type="text"
                    className={cl.search}
                    placeholder="Поиск..."
                    value={searchQuery}
                    onChange={handleSearchChange}
                />
            </div>

            <div className={cl.filters}>
                <div className={cl.dropdown}>
                    <button
                        className={cl.filterBtn}
                        onClick={() => toggleMenu("category")}
                    >
                        {selectedCategory}
                    </button>
                    <div
                        className={`${cl.dropdownMenu} ${
                            openMenu === "category" ? cl.show : ""
                        }`}
                    >
                        {categories.map((category, index) => (
                            <div
                                key={index}
                                className={cl.dropdownItem}
                                onClick={() => selectCategory(category)}
                            >
                                {category}
                            </div>
                        ))}
                    </div>
                </div>

                <div className={cl.dropdown}>
                    <button
                        className={cl.filterBtn}
                        onClick={() => toggleMenu("source")}
                    >
                        {selectedSource}
                    </button>
                    <div
                        className={`${cl.dropdownMenu} ${
                            openMenu === "source" ? cl.show : ""
                        }`}
                    >
                        <div className={cl.dropdownItem} onClick={() => selectSource("Все")}>Все</div>
                        <div className={cl.dropdownItem} onClick={() => selectSource("Наука.рф")}>Наука.рф</div>
                    </div>
                </div>
            </div>

            <div className={cl.articles}>
                <ArticleItem
                    searchQuery={searchQuery}
                    selectedCategory={selectedCategory}
                    selectedSource={selectedSource}
                />
            </div>

            <div className={cl.recommendationsSection}>
                <h2>Рекомендованные публикации</h2>
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
                            className={cl.recommendationImage}
                            />
                            <p className={cl.recText}>{rec.title}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default MainPage