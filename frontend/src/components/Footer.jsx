import React from "react";
import cl from '../styles/Footer.module.css'
import githubIcon from '../UI/icons/githubIcon.png'
import kolpaknews from '../UI/icons/kolpaknews.svg'

const Footer = () => {
    return (
        <div className={cl.container}>
            <div className={cl.content}>
                <div className={cl.about}>
                    <img className={cl.telegram} src={kolpaknews} alt="kolpak" />
                    <p>© 2025 - 2025 Jacobs Колпак</p>
                    <a href="https://github.com/FlexonaFFt/XackatonKolpaki2025" target="_blank" rel="noopener noreferrer">
                        <img className={cl.telegram} src={githubIcon} alt="GitHub" />
                    </a>
                </div>
                <hr />
                <div className={cl.links}>
                    <div className={cl.wrap}>
                        <p>Власюк Данил Team Lead</p>
                        <a href="https://t.me/hhrrjjss">Link Telegram</a>
                    </div>
                    <div className={cl.wrap}>
                        <p>Яковенко Максим UI/UX Designer</p>
                        <a href="https://t.me/ykvnkm">Link Telegram</a>
                    </div>
                    <div className={cl.wrap}>
                        <p>Беспалый Максим Frontend Developer</p>
                        <a href="https://t.me/kxwarvta">Link Telegram</a>
                    </div>
                    <div className={cl.wrap}>
                        <p>Жаров Игорь Backend Developer</p>
                        <a href="https://t.me/FlexonaFFt">Link Telegram</a>
                    </div>
                    <div className={cl.wrap}>
                        <p>Скрыпник Михаил ML-Engineer</p>
                        <a href="https://t.me/mskry13">Link Telegram</a>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Footer