/**
 * MobileForm.jsx
 * Personal Recipe Intelligence
 * モバイル最適化入力フォームコンポーネント
 * - キーボード対応
 * - オートコンプリート
 * - タッチ最適化
 */

import React, { useState, useRef, useEffect } from 'react';

/**
 * モバイル最適化フォームコンポーネント
 * @param {Object} props - コンポーネントプロパティ
 * @param {Object} props.initialData - 初期データ
 * @param {Function} props.onSubmit - 送信ハンドラー
 * @param {Function} props.onCancel - キャンセルハンドラー
 */
const MobileForm = ({ initialData = {}, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    title: initialData.title || '',
    description: initialData.description || '',
    cookTime: initialData.cookTime || '',
    servings: initialData.servings || '',
    difficulty: initialData.difficulty || 'medium',
    tags: initialData.tags || [],
    ingredients: initialData.ingredients || [],
    steps: initialData.steps || [],
    ...initialData,
  });

  const [currentTag, setCurrentTag] = useState('');
  const [tagSuggestions, setTagSuggestions] = useState([]);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const formRef = useRef(null);
  const titleInputRef = useRef(null);

  // よく使われるタグのサンプル
  const popularTags = [
    '和食',
    '洋食',
    '中華',
    'イタリアン',
    '簡単',
    '時短',
    'ヘルシー',
    'おつまみ',
    'お弁当',
    'スイーツ',
    'パーティー',
    '作り置き',
  ];

  // 初回レンダリング時にタイトルにフォーカス
  useEffect(() => {
    if (titleInputRef.current) {
      titleInputRef.current.focus();
    }
  }, []);

  // フォームデータの更新
  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    // エラーをクリア
    if (errors[field]) {
      setErrors((prev) => ({
        ...prev,
        [field]: null,
      }));
    }
  };

  // タグの追加
  const handleAddTag = (tag) => {
    const trimmedTag = tag.trim();
    if (trimmedTag && !formData.tags.includes(trimmedTag)) {
      setFormData((prev) => ({
        ...prev,
        tags: [...prev.tags, trimmedTag],
      }));
    }
    setCurrentTag('');
    setTagSuggestions([]);
  };

  // タグの削除
  const handleRemoveTag = (index) => {
    setFormData((prev) => ({
      ...prev,
      tags: prev.tags.filter((_, i) => i !== index),
    }));
  };

  // タグ入力の変更
  const handleTagInputChange = (value) => {
    setCurrentTag(value);

    // サジェスト表示
    if (value.length > 0) {
      const suggestions = popularTags.filter(
        (tag) =>
          tag.toLowerCase().includes(value.toLowerCase()) &&
          !formData.tags.includes(tag)
      );
      setTagSuggestions(suggestions);
    } else {
      setTagSuggestions([]);
    }
  };

  // タグ入力のキーダウン
  const handleTagKeyDown = (e) => {
    if (e.key === 'Enter' && currentTag.trim()) {
      e.preventDefault();
      handleAddTag(currentTag);
    }
  };

  // 材料の追加
  const handleAddIngredient = () => {
    setFormData((prev) => ({
      ...prev,
      ingredients: [...prev.ingredients, { name: '', amount: '' }],
    }));
  };

  // 材料の更新
  const handleIngredientChange = (index, field, value) => {
    setFormData((prev) => ({
      ...prev,
      ingredients: prev.ingredients.map((ingredient, i) =>
        i === index ? { ...ingredient, [field]: value } : ingredient
      ),
    }));
  };

  // 材料の削除
  const handleRemoveIngredient = (index) => {
    setFormData((prev) => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index),
    }));
  };

  // 手順の追加
  const handleAddStep = () => {
    setFormData((prev) => ({
      ...prev,
      steps: [...prev.steps, ''],
    }));
  };

  // 手順の更新
  const handleStepChange = (index, value) => {
    setFormData((prev) => ({
      ...prev,
      steps: prev.steps.map((step, i) => (i === index ? value : step)),
    }));
  };

  // 手順の削除
  const handleRemoveStep = (index) => {
    setFormData((prev) => ({
      ...prev,
      steps: prev.steps.filter((_, i) => i !== index),
    }));
  };

  // バリデーション
  const validate = () => {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'タイトルは必須です';
    }

    if (formData.cookTime && isNaN(formData.cookTime)) {
      newErrors.cookTime = '調理時間は数値で入力してください';
    }

    if (formData.servings && isNaN(formData.servings)) {
      newErrors.servings = '人数は数値で入力してください';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // フォーム送信
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);

    try {
      if (onSubmit) {
        await onSubmit(formData);
      }
    } catch (error) {
      console.error('フォーム送信エラー:', error);
      setErrors({ submit: 'エラーが発生しました。もう一度お試しください。' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form ref={formRef} className="mobile-form" onSubmit={handleSubmit}>
      {/* タイトル */}
      <div className="form-group">
        <label htmlFor="title" className="form-label required">
          タイトル
        </label>
        <input
          ref={titleInputRef}
          type="text"
          id="title"
          className={`input ${errors.title ? 'input-error' : ''}`}
          value={formData.title}
          onChange={(e) => handleChange('title', e.target.value)}
          placeholder="例: チキンカレー"
          autoComplete="off"
          required
        />
        {errors.title && <p className="form-error">{errors.title}</p>}
      </div>

      {/* 説明 */}
      <div className="form-group">
        <label htmlFor="description" className="form-label">
          説明
        </label>
        <textarea
          id="description"
          className="textarea"
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          placeholder="レシピの簡単な説明を入力してください"
          rows="3"
        />
      </div>

      {/* メタ情報グリッド */}
      <div className="form-grid">
        {/* 調理時間 */}
        <div className="form-group">
          <label htmlFor="cookTime" className="form-label">
            調理時間（分）
          </label>
          <input
            type="number"
            id="cookTime"
            className={`input ${errors.cookTime ? 'input-error' : ''}`}
            value={formData.cookTime}
            onChange={(e) => handleChange('cookTime', e.target.value)}
            placeholder="30"
            min="1"
            inputMode="numeric"
          />
          {errors.cookTime && <p className="form-error">{errors.cookTime}</p>}
        </div>

        {/* 人数 */}
        <div className="form-group">
          <label htmlFor="servings" className="form-label">
            人数
          </label>
          <input
            type="number"
            id="servings"
            className={`input ${errors.servings ? 'input-error' : ''}`}
            value={formData.servings}
            onChange={(e) => handleChange('servings', e.target.value)}
            placeholder="2"
            min="1"
            inputMode="numeric"
          />
          {errors.servings && <p className="form-error">{errors.servings}</p>}
        </div>

        {/* 難易度 */}
        <div className="form-group">
          <label htmlFor="difficulty" className="form-label">
            難易度
          </label>
          <select
            id="difficulty"
            className="select"
            value={formData.difficulty}
            onChange={(e) => handleChange('difficulty', e.target.value)}
          >
            <option value="easy">簡単</option>
            <option value="medium">普通</option>
            <option value="hard">難しい</option>
          </select>
        </div>
      </div>

      {/* タグ */}
      <div className="form-group">
        <label htmlFor="tags" className="form-label">
          タグ
        </label>
        <div className="tag-input-wrapper">
          <input
            type="text"
            id="tags"
            className="input"
            value={currentTag}
            onChange={(e) => handleTagInputChange(e.target.value)}
            onKeyDown={handleTagKeyDown}
            placeholder="タグを入力してEnter"
            autoComplete="off"
          />
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => handleAddTag(currentTag)}
            disabled={!currentTag.trim()}
          >
            追加
          </button>
        </div>

        {/* タグサジェスト */}
        {tagSuggestions.length > 0 && (
          <div className="tag-suggestions">
            {tagSuggestions.map((tag) => (
              <button
                key={tag}
                type="button"
                className="tag-suggestion"
                onClick={() => handleAddTag(tag)}
              >
                {tag}
              </button>
            ))}
          </div>
        )}

        {/* タグリスト */}
        {formData.tags.length > 0 && (
          <div className="tag-list">
            {formData.tags.map((tag, index) => (
              <span key={index} className="tag-item">
                {tag}
                <button
                  type="button"
                  className="tag-remove"
                  onClick={() => handleRemoveTag(index)}
                  aria-label={`${tag}を削除`}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* 材料 */}
      <div className="form-group">
        <div className="form-label-with-action">
          <label className="form-label">材料</label>
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={handleAddIngredient}
          >
            + 追加
          </button>
        </div>

        <div className="ingredient-list">
          {formData.ingredients.map((ingredient, index) => (
            <div key={index} className="ingredient-item">
              <input
                type="text"
                className="input input-sm"
                value={ingredient.name}
                onChange={(e) =>
                  handleIngredientChange(index, 'name', e.target.value)
                }
                placeholder="材料名"
              />
              <input
                type="text"
                className="input input-sm"
                value={ingredient.amount}
                onChange={(e) =>
                  handleIngredientChange(index, 'amount', e.target.value)
                }
                placeholder="分量"
              />
              <button
                type="button"
                className="btn btn-icon btn-sm"
                onClick={() => handleRemoveIngredient(index)}
                aria-label="削除"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 手順 */}
      <div className="form-group">
        <div className="form-label-with-action">
          <label className="form-label">手順</label>
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={handleAddStep}
          >
            + 追加
          </button>
        </div>

        <div className="step-list">
          {formData.steps.map((step, index) => (
            <div key={index} className="step-item">
              <div className="step-number">{index + 1}</div>
              <textarea
                className="textarea textarea-sm"
                value={step}
                onChange={(e) => handleStepChange(index, e.target.value)}
                placeholder="手順を入力してください"
                rows="2"
              />
              <button
                type="button"
                className="btn btn-icon btn-sm"
                onClick={() => handleRemoveStep(index)}
                aria-label="削除"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* エラーメッセージ */}
      {errors.submit && (
        <div className="form-error-message">{errors.submit}</div>
      )}

      {/* アクションボタン */}
      <div className="form-actions">
        <button
          type="button"
          className="btn btn-outline"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          キャンセル
        </button>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? '保存中...' : '保存'}
        </button>
      </div>

      <style jsx>{`
        /* ========================================
           Form Base
           ======================================== */
        .mobile-form {
          width: 100%;
          max-width: 100%;
          padding: 1rem;
        }

        .form-group {
          margin-bottom: 1.5rem;
        }

        .form-label {
          display: block;
          margin-bottom: 0.5rem;
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--color-text, #1f2937);
        }

        .form-label.required::after {
          content: ' *';
          color: var(--color-error, #ef4444);
        }

        .form-label-with-action {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 0.5rem;
        }

        .form-error {
          margin-top: 0.25rem;
          font-size: 0.8125rem;
          color: var(--color-error, #ef4444);
        }

        .form-error-message {
          padding: 0.75rem;
          margin-bottom: 1rem;
          background-color: #fee2e2;
          border-left: 4px solid var(--color-error, #ef4444);
          border-radius: 0.375rem;
          color: #991b1b;
          font-size: 0.875rem;
        }

        /* ========================================
           Input Components
           ======================================== */
        .input,
        .textarea,
        .select {
          width: 100%;
          padding: 0.75rem;
          font-size: 1rem;
          line-height: 1.5;
          color: var(--color-text, #1f2937);
          background-color: var(--color-background, #ffffff);
          border: 2px solid var(--color-border, #e5e7eb);
          border-radius: 0.5rem;
          transition: border-color 0.15s ease-in-out;
        }

        .input:focus,
        .textarea:focus,
        .select:focus {
          outline: none;
          border-color: var(--color-primary, #4f46e5);
          box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }

        .input-error {
          border-color: var(--color-error, #ef4444);
        }

        .input-sm {
          padding: 0.5rem 0.75rem;
          font-size: 0.875rem;
        }

        .textarea {
          min-height: 100px;
          resize: vertical;
        }

        .textarea-sm {
          min-height: 60px;
        }

        /* ========================================
           Form Grid
           ======================================== */
        .form-grid {
          display: grid;
          gap: 1rem;
          grid-template-columns: 1fr;
        }

        @media (min-width: 480px) {
          .form-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        @media (min-width: 768px) {
          .form-grid {
            grid-template-columns: repeat(3, 1fr);
          }

          .mobile-form {
            padding: 1.5rem;
          }
        }

        /* ========================================
           Tags
           ======================================== */
        .tag-input-wrapper {
          display: flex;
          gap: 0.5rem;
        }

        .tag-input-wrapper .input {
          flex: 1;
        }

        .tag-suggestions {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-top: 0.5rem;
        }

        .tag-suggestion {
          padding: 0.375rem 0.75rem;
          background-color: var(--color-surface, #f9fafb);
          border: 1px solid var(--color-border, #e5e7eb);
          border-radius: 0.375rem;
          font-size: 0.875rem;
          color: var(--color-text, #1f2937);
          cursor: pointer;
          transition: all 0.15s ease-in-out;
        }

        .tag-suggestion:hover {
          background-color: var(--color-primary, #4f46e5);
          color: white;
          border-color: var(--color-primary, #4f46e5);
        }

        .tag-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-top: 0.5rem;
        }

        .tag-item {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          padding: 0.375rem 0.75rem;
          background-color: var(--color-primary, #4f46e5);
          color: white;
          border-radius: 0.375rem;
          font-size: 0.875rem;
        }

        .tag-remove {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 20px;
          height: 20px;
          padding: 0;
          background: none;
          border: none;
          color: white;
          font-size: 1.25rem;
          line-height: 1;
          cursor: pointer;
          opacity: 0.8;
          transition: opacity 0.15s ease-in-out;
        }

        .tag-remove:hover {
          opacity: 1;
        }

        /* ========================================
           Ingredients
           ======================================== */
        .ingredient-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .ingredient-item {
          display: grid;
          grid-template-columns: 1fr 100px auto;
          gap: 0.5rem;
          align-items: center;
        }

        /* ========================================
           Steps
           ======================================== */
        .step-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .step-item {
          display: grid;
          grid-template-columns: 32px 1fr auto;
          gap: 0.5rem;
          align-items: start;
        }

        .step-number {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          background-color: var(--color-primary, #4f46e5);
          color: white;
          border-radius: 50%;
          font-size: 0.875rem;
          font-weight: 600;
          flex-shrink: 0;
        }

        /* ========================================
           Buttons
           ======================================== */
        .btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-height: 44px;
          padding: 0.75rem 1.5rem;
          font-size: 1rem;
          font-weight: 500;
          border: none;
          border-radius: 0.5rem;
          cursor: pointer;
          transition: all 0.15s ease-in-out;
          user-select: none;
        }

        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-sm {
          min-height: 36px;
          padding: 0.5rem 1rem;
          font-size: 0.875rem;
        }

        .btn-primary {
          background-color: var(--color-primary, #4f46e5);
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background-color: #4338ca;
        }

        .btn-secondary {
          background-color: var(--color-secondary, #06b6d4);
          color: white;
        }

        .btn-secondary:hover:not(:disabled) {
          background-color: #0891b2;
        }

        .btn-outline {
          background-color: transparent;
          border: 2px solid var(--color-border, #e5e7eb);
          color: var(--color-text, #1f2937);
        }

        .btn-outline:hover:not(:disabled) {
          background-color: var(--color-surface, #f9fafb);
        }

        .btn-icon {
          min-width: 36px;
          padding: 0.5rem;
        }

        /* ========================================
           Form Actions
           ======================================== */
        .form-actions {
          display: flex;
          gap: 0.75rem;
          margin-top: 2rem;
          padding-top: 1.5rem;
          border-top: 1px solid var(--color-border, #e5e7eb);
        }

        .form-actions .btn {
          flex: 1;
        }

        @media (min-width: 768px) {
          .form-actions {
            justify-content: flex-end;
          }

          .form-actions .btn {
            flex: 0 0 auto;
            min-width: 120px;
          }
        }
      `}</style>
    </form>
  );
};

export default MobileForm;
