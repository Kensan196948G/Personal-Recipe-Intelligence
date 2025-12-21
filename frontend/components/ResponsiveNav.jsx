/**
 * ResponsiveNav.jsx
 * Personal Recipe Intelligence
 * レスポンシブナビゲーションコンポーネント
 * - ハンバーガーメニュー（モバイル）
 * - サイドバー（タブレット以上）
 * - タブバー（モバイル下部固定）
 */

import React, { useState, useEffect } from 'react';

/**
 * レスポンシブナビゲーションコンポーネント
 * @param {Object} props - コンポーネントプロパティ
 * @param {Array} props.menuItems - メニューアイテム配列
 * @param {string} props.activeRoute - 現在のアクティブルート
 * @param {Function} props.onNavigate - ナビゲーションハンドラー
 */
const ResponsiveNav = ({ menuItems = [], activeRoute = '/', onNavigate }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // 画面サイズの監視
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // モバイルメニューのトグル
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // メニュークリック時
  const handleMenuClick = (route) => {
    if (onNavigate) {
      onNavigate(route);
    }
    setIsMobileMenuOpen(false);
  };

  // ボディのスクロール制御
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isMobileMenuOpen]);

  return (
    <>
      {/* ヘッダーナビゲーション */}
      <header className="nav-header">
        <div className="nav-container">
          {/* ロゴ */}
          <div className="nav-logo">
            <button
              onClick={() => handleMenuClick('/')}
              className="logo-button"
              aria-label="ホームへ移動"
            >
              <svg
                width="32"
                height="32"
                viewBox="0 0 32 32"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M16 2L4 12H8V28H14V20H18V28H24V12H28L16 2Z"
                  fill="currentColor"
                />
              </svg>
              <span className="logo-text">Recipe Intelligence</span>
            </button>
          </div>

          {/* デスクトップメニュー */}
          <nav className="nav-desktop" aria-label="デスクトップナビゲーション">
            {menuItems.map((item) => (
              <button
                key={item.route}
                onClick={() => handleMenuClick(item.route)}
                className={`nav-item ${activeRoute === item.route ? 'active' : ''}`}
                aria-current={activeRoute === item.route ? 'page' : undefined}
              >
                {item.icon && <span className="nav-icon">{item.icon}</span>}
                <span className="nav-label">{item.label}</span>
              </button>
            ))}
          </nav>

          {/* ハンバーガーメニューボタン（モバイル） */}
          <button
            className="hamburger-button"
            onClick={toggleMobileMenu}
            aria-label={isMobileMenuOpen ? 'メニューを閉じる' : 'メニューを開く'}
            aria-expanded={isMobileMenuOpen}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              {isMobileMenuOpen ? (
                <>
                  <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </>
              ) : (
                <>
                  <path d="M4 6H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <path d="M4 12H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <path d="M4 18H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </>
              )}
            </svg>
          </button>
        </div>
      </header>

      {/* モバイルメニュー（サイドバー） */}
      {isMobileMenuOpen && (
        <>
          <div
            className="mobile-menu-backdrop"
            onClick={toggleMobileMenu}
            aria-hidden="true"
          />
          <nav
            className="mobile-menu"
            aria-label="モバイルナビゲーション"
          >
            <div className="mobile-menu-header">
              <h2>メニュー</h2>
              <button
                onClick={toggleMobileMenu}
                className="close-button"
                aria-label="メニューを閉じる"
              >
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </button>
            </div>
            <ul className="mobile-menu-list">
              {menuItems.map((item) => (
                <li key={item.route}>
                  <button
                    onClick={() => handleMenuClick(item.route)}
                    className={`mobile-menu-item ${activeRoute === item.route ? 'active' : ''}`}
                    aria-current={activeRoute === item.route ? 'page' : undefined}
                  >
                    {item.icon && <span className="mobile-menu-icon">{item.icon}</span>}
                    <span className="mobile-menu-label">{item.label}</span>
                  </button>
                </li>
              ))}
            </ul>
          </nav>
        </>
      )}

      {/* タブバー（モバイル下部固定） */}
      {isMobile && (
        <nav className="tab-bar" aria-label="タブバーナビゲーション">
          {menuItems.slice(0, 4).map((item) => (
            <button
              key={item.route}
              onClick={() => handleMenuClick(item.route)}
              className={`tab-item ${activeRoute === item.route ? 'active' : ''}`}
              aria-current={activeRoute === item.route ? 'page' : undefined}
            >
              {item.icon && <span className="tab-icon">{item.icon}</span>}
              <span className="tab-label">{item.label}</span>
            </button>
          ))}
        </nav>
      )}

      <style jsx>{`
        /* ========================================
           Header Navigation
           ======================================== */
        .nav-header {
          position: sticky;
          top: 0;
          z-index: var(--z-sticky, 1020);
          background-color: var(--color-background, #ffffff);
          border-bottom: 1px solid var(--color-border, #e5e7eb);
          box-shadow: var(--shadow-sm, 0 1px 2px 0 rgba(0, 0, 0, 0.05));
        }

        .nav-container {
          display: flex;
          align-items: center;
          justify-content: space-between;
          max-width: 1200px;
          margin: 0 auto;
          padding: 0.75rem 1rem;
        }

        /* Logo */
        .nav-logo {
          flex-shrink: 0;
        }

        .logo-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem;
          background: none;
          border: none;
          color: var(--color-primary, #4f46e5);
          font-size: 1.125rem;
          font-weight: 700;
          cursor: pointer;
          transition: opacity 0.15s ease-in-out;
        }

        .logo-button:hover {
          opacity: 0.8;
        }

        .logo-text {
          display: none;
        }

        /* Desktop Navigation */
        .nav-desktop {
          display: none;
        }

        /* Hamburger Button */
        .hamburger-button {
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 44px;
          min-height: 44px;
          padding: 0.5rem;
          background: none;
          border: none;
          color: var(--color-text, #1f2937);
          cursor: pointer;
          transition: color 0.15s ease-in-out;
        }

        .hamburger-button:hover {
          color: var(--color-primary, #4f46e5);
        }

        /* ========================================
           Mobile Menu (Sidebar)
           ======================================== */
        .mobile-menu-backdrop {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: var(--z-modal-backdrop, 1040);
          background-color: rgba(0, 0, 0, 0.5);
          animation: fadeIn 0.25s ease-in-out;
        }

        .mobile-menu {
          position: fixed;
          top: 0;
          right: 0;
          bottom: 0;
          z-index: var(--z-modal, 1050);
          width: 280px;
          max-width: 85%;
          background-color: var(--color-background, #ffffff);
          box-shadow: var(--shadow-lg, 0 10px 15px -3px rgba(0, 0, 0, 0.1));
          overflow-y: auto;
          animation: slideInRight 0.25s ease-in-out;
        }

        @keyframes slideInRight {
          from {
            transform: translateX(100%);
          }
          to {
            transform: translateX(0);
          }
        }

        .mobile-menu-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1rem;
          border-bottom: 1px solid var(--color-border, #e5e7eb);
        }

        .mobile-menu-header h2 {
          margin: 0;
          font-size: 1.125rem;
          font-weight: 600;
        }

        .close-button {
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 44px;
          min-height: 44px;
          padding: 0.5rem;
          background: none;
          border: none;
          color: var(--color-text, #1f2937);
          cursor: pointer;
        }

        .mobile-menu-list {
          list-style: none;
          padding: 0.5rem 0;
          margin: 0;
        }

        .mobile-menu-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          width: 100%;
          min-height: 48px;
          padding: 0.75rem 1rem;
          background: none;
          border: none;
          color: var(--color-text, #1f2937);
          font-size: 1rem;
          text-align: left;
          cursor: pointer;
          transition: background-color 0.15s ease-in-out;
        }

        .mobile-menu-item:hover {
          background-color: var(--color-surface, #f9fafb);
        }

        .mobile-menu-item.active {
          color: var(--color-primary, #4f46e5);
          background-color: rgba(79, 70, 229, 0.1);
          font-weight: 600;
        }

        .mobile-menu-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
        }

        /* ========================================
           Tab Bar (Mobile Bottom)
           ======================================== */
        .tab-bar {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          z-index: var(--z-fixed, 1030);
          display: flex;
          background-color: var(--color-background, #ffffff);
          border-top: 1px solid var(--color-border, #e5e7eb);
          box-shadow: 0 -1px 3px 0 rgba(0, 0, 0, 0.1);
          padding-bottom: env(safe-area-inset-bottom);
        }

        .tab-item {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 0.25rem;
          min-height: 56px;
          padding: 0.5rem;
          background: none;
          border: none;
          color: var(--color-text-secondary, #6b7280);
          font-size: 0.75rem;
          cursor: pointer;
          transition: color 0.15s ease-in-out;
        }

        .tab-item:hover {
          color: var(--color-text, #1f2937);
        }

        .tab-item.active {
          color: var(--color-primary, #4f46e5);
          font-weight: 600;
        }

        .tab-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
        }

        .tab-label {
          font-size: 0.75rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          max-width: 100%;
        }

        /* ========================================
           Responsive Styles
           ======================================== */

        /* 480px - Small Mobile */
        @media (min-width: 480px) {
          .logo-text {
            display: inline;
          }
        }

        /* 768px - Tablet */
        @media (min-width: 768px) {
          .hamburger-button {
            display: none;
          }

          .nav-desktop {
            display: flex;
            gap: 0.5rem;
          }

          .nav-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            min-height: 44px;
            padding: 0.5rem 1rem;
            background: none;
            border: none;
            border-radius: 0.5rem;
            color: var(--color-text, #1f2937);
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.15s ease-in-out;
          }

          .nav-item:hover {
            background-color: var(--color-surface, #f9fafb);
          }

          .nav-item.active {
            color: var(--color-primary, #4f46e5);
            background-color: rgba(79, 70, 229, 0.1);
          }

          .nav-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
          }
        }
      `}</style>
    </>
  );
};

export default ResponsiveNav;
