import React, { useState, useEffect } from 'react';

/**
 * 宅配サービス連携コンポーネント
 */
const DeliveryIntegration = ({ ingredients = [] }) => {
  const [services, setServices] = useState([]);
  const [selectedService, setSelectedService] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [priceComparison, setPriceComparison] = useState(null);
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentIngredient, setCurrentIngredient] = useState(null);

  // サービス一覧取得
  useEffect(() => {
    fetchServices();
  }, []);

  // カート取得（サービス選択時）
  useEffect(() => {
    if (selectedService) {
      fetchCart();
    }
  }, [selectedService]);

  const fetchServices = async () => {
    try {
      const response = await fetch('/api/v1/delivery/services');
      const data = await response.json();
      if (data.status === 'ok') {
        setServices(data.data.services);
        if (data.data.services.length > 0) {
          setSelectedService(data.data.services[0].id);
        }
      }
    } catch (err) {
      console.error('Failed to fetch services:', err);
      setError('サービス一覧の取得に失敗しました');
    }
  };

  const fetchCart = async () => {
    if (!selectedService) return;

    try {
      const response = await fetch(`/api/v1/delivery/cart?service=${selectedService}`);
      const data = await response.json();
      if (data.status === 'ok') {
        setCart(data.data);
      }
    } catch (err) {
      console.error('Failed to fetch cart:', err);
    }
  };

  const searchProducts = async (ingredientName) => {
    setLoading(true);
    setError(null);
    setCurrentIngredient(ingredientName);

    try {
      const response = await fetch('/api/v1/delivery/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ingredient_name: ingredientName,
          services: selectedService ? [selectedService] : null,
          max_results: 20
        })
      });

      const data = await response.json();
      if (data.status === 'ok') {
        setSearchResults(data.data.products);
      }
    } catch (err) {
      console.error('Failed to search products:', err);
      setError('商品検索に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const comparePrice = async (ingredientName) => {
    setLoading(true);
    setError(null);
    setCurrentIngredient(ingredientName);

    try {
      const response = await fetch(
        `/api/v1/delivery/price-compare?ingredient_name=${encodeURIComponent(ingredientName)}`
      );

      const data = await response.json();
      if (data.status === 'ok') {
        setPriceComparison(data.data);
        setSearchResults(data.data.products);
      }
    } catch (err) {
      console.error('Failed to compare prices:', err);
      setError('価格比較に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (productId) => {
    if (!selectedService) {
      setError('サービスを選択してください');
      return;
    }

    try {
      const response = await fetch('/api/v1/delivery/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service: selectedService,
          product_id: productId,
          quantity: 1
        })
      });

      const data = await response.json();
      if (data.status === 'ok') {
        setCart(data.data.cart);
        alert('カートに追加しました');
      }
    } catch (err) {
      console.error('Failed to add to cart:', err);
      setError('カートへの追加に失敗しました');
    }
  };

  const removeFromCart = async (productId) => {
    if (!selectedService) return;

    try {
      const response = await fetch('/api/v1/delivery/cart', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service: selectedService,
          product_id: productId
        })
      });

      const data = await response.json();
      if (data.status === 'ok') {
        setCart(data.data.cart);
      }
    } catch (err) {
      console.error('Failed to remove from cart:', err);
      setError('カートからの削除に失敗しました');
    }
  };

  const clearCart = async () => {
    if (!selectedService) return;
    if (!confirm('カートをクリアしますか？')) return;

    try {
      const response = await fetch(
        `/api/v1/delivery/cart/clear?service=${selectedService}`,
        { method: 'DELETE' }
      );

      const data = await response.json();
      if (data.status === 'ok') {
        setCart(data.data.cart);
      }
    } catch (err) {
      console.error('Failed to clear cart:', err);
      setError('カートのクリアに失敗しました');
    }
  };

  const goToCheckout = async () => {
    if (!selectedService) return;

    try {
      const response = await fetch(
        `/api/v1/delivery/checkout-url?service=${selectedService}`,
        { method: 'POST' }
      );

      const data = await response.json();
      if (data.status === 'ok') {
        window.open(data.data.checkout_url, '_blank');
      }
    } catch (err) {
      console.error('Failed to generate checkout URL:', err);
      setError('注文ページの生成に失敗しました');
    }
  };

  const getServiceInfo = (serviceId) => {
    return services.find(s => s.id === serviceId);
  };

  return (
    <div className="delivery-integration">
      <h2>宅配サービス連携</h2>

      {error && (
        <div className="alert alert-error">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* サービス選択 */}
      <div className="service-selector">
        <label>配送サービス:</label>
        <select
          value={selectedService || ''}
          onChange={(e) => setSelectedService(e.target.value)}
        >
          {services.map(service => (
            <option key={service.id} value={service.id}>
              {service.name}
            </option>
          ))}
        </select>
        {selectedService && (
          <div className="service-info">
            <small>
              {getServiceInfo(selectedService)?.description}
              {' | '}
              配送料: ¥{getServiceInfo(selectedService)?.delivery_fee}
              {getServiceInfo(selectedService)?.free_shipping_threshold && (
                <> (¥{getServiceInfo(selectedService).free_shipping_threshold}以上で無料)</>
              )}
            </small>
          </div>
        )}
      </div>

      {/* 食材リストから検索 */}
      {ingredients.length > 0 && (
        <div className="ingredient-list">
          <h3>レシピの食材</h3>
          <div className="ingredient-buttons">
            {ingredients.map((ingredient, index) => (
              <button
                key={index}
                className="btn btn-sm"
                onClick={() => searchProducts(ingredient.name)}
                disabled={loading}
              >
                {ingredient.name}
              </button>
            ))}
          </div>
          <button
            className="btn btn-primary"
            onClick={() => {
              ingredients.forEach(ing => comparePrice(ing.name));
            }}
            disabled={loading}
          >
            すべての食材を価格比較
          </button>
        </div>
      )}

      {/* 検索結果 */}
      {loading && <div className="loading">検索中...</div>}

      {searchResults.length > 0 && (
        <div className="search-results">
          <h3>
            {currentIngredient} の検索結果
            {priceComparison && (
              <span className="price-range">
                {' '}(¥{priceComparison.price_range.min} - ¥{priceComparison.price_range.max})
              </span>
            )}
          </h3>

          {/* 最安値表示 */}
          {priceComparison?.best_price && (
            <div className="best-price">
              <strong>最安値:</strong> {priceComparison.best_price.product.name}
              {' - '}
              ¥{priceComparison.best_price.price}
              {' '}({priceComparison.best_price.service})
            </div>
          )}

          <div className="product-grid">
            {searchResults.map(product => (
              <div key={product.id} className="product-card">
                <div className="product-header">
                  <span className="service-badge">{product.service}</span>
                  {!product.in_stock && (
                    <span className="stock-badge out-of-stock">在庫なし</span>
                  )}
                </div>
                <h4>{product.name}</h4>
                {product.brand && (
                  <div className="product-brand">{product.brand}</div>
                )}
                <div className="product-price">
                  ¥{product.price}
                  <span className="product-unit">/{product.unit}</span>
                </div>
                <div className="product-actions">
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => addToCart(product.id)}
                    disabled={!product.in_stock}
                  >
                    カートに追加
                  </button>
                  {product.product_url && (
                    <a
                      href={product.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-sm"
                    >
                      商品ページ
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* カート */}
      {cart && cart.items.length > 0 && (
        <div className="cart">
          <h3>カート ({cart.item_count}件)</h3>
          <div className="cart-items">
            {cart.items.map((item, index) => (
              <div key={index} className="cart-item">
                <div className="cart-item-info">
                  <div className="cart-item-name">{item.product.name}</div>
                  <div className="cart-item-meta">
                    {item.product.brand && <span>{item.product.brand}</span>}
                    <span>×{item.quantity}</span>
                  </div>
                </div>
                <div className="cart-item-price">
                  ¥{item.product.price * item.quantity}
                </div>
                <button
                  className="btn btn-sm btn-danger"
                  onClick={() => removeFromCart(item.product.id)}
                >
                  削除
                </button>
              </div>
            ))}
          </div>
          <div className="cart-total">
            <strong>合計:</strong> ¥{cart.total_price}
          </div>
          <div className="cart-actions">
            <button className="btn btn-primary" onClick={goToCheckout}>
              注文ページへ
            </button>
            <button className="btn btn-secondary" onClick={clearCart}>
              カートをクリア
            </button>
          </div>
        </div>
      )}

      <style jsx>{`
        .delivery-integration {
          padding: 20px;
        }

        .alert {
          padding: 12px;
          border-radius: 4px;
          margin-bottom: 16px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .alert-error {
          background-color: #fee;
          color: #c00;
          border: 1px solid #fcc;
        }

        .service-selector {
          margin-bottom: 20px;
        }

        .service-selector label {
          display: block;
          margin-bottom: 8px;
          font-weight: 600;
        }

        .service-selector select {
          width: 100%;
          max-width: 400px;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .service-info {
          margin-top: 8px;
          color: #666;
        }

        .ingredient-list {
          margin-bottom: 24px;
          padding: 16px;
          background-color: #f9f9f9;
          border-radius: 8px;
        }

        .ingredient-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 12px;
        }

        .loading {
          text-align: center;
          padding: 20px;
          color: #666;
        }

        .search-results {
          margin-bottom: 24px;
        }

        .price-range {
          font-size: 0.9em;
          color: #666;
        }

        .best-price {
          padding: 12px;
          background-color: #ffc;
          border: 1px solid #fc0;
          border-radius: 4px;
          margin-bottom: 16px;
        }

        .product-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 16px;
        }

        .product-card {
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 16px;
          background-color: #fff;
        }

        .product-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
        }

        .service-badge {
          background-color: #007bff;
          color: white;
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 0.8em;
        }

        .stock-badge {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 0.8em;
        }

        .out-of-stock {
          background-color: #ccc;
          color: #666;
        }

        .product-brand {
          font-size: 0.9em;
          color: #666;
          margin-bottom: 4px;
        }

        .product-price {
          font-size: 1.5em;
          font-weight: 600;
          color: #c00;
          margin: 8px 0;
        }

        .product-unit {
          font-size: 0.6em;
          color: #666;
        }

        .product-actions {
          display: flex;
          gap: 8px;
          margin-top: 12px;
        }

        .cart {
          border: 2px solid #007bff;
          border-radius: 8px;
          padding: 20px;
          background-color: #f0f8ff;
        }

        .cart-items {
          margin-bottom: 16px;
        }

        .cart-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          background-color: white;
          border-radius: 4px;
          margin-bottom: 8px;
        }

        .cart-item-info {
          flex: 1;
        }

        .cart-item-name {
          font-weight: 600;
          margin-bottom: 4px;
        }

        .cart-item-meta {
          font-size: 0.9em;
          color: #666;
        }

        .cart-item-meta span {
          margin-right: 12px;
        }

        .cart-item-price {
          font-weight: 600;
          margin: 0 16px;
        }

        .cart-total {
          text-align: right;
          font-size: 1.2em;
          padding: 12px 0;
          border-top: 2px solid #007bff;
        }

        .cart-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          margin-top: 16px;
        }

        .btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: opacity 0.2s;
        }

        .btn:hover {
          opacity: 0.8;
        }

        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-primary {
          background-color: #007bff;
          color: white;
        }

        .btn-secondary {
          background-color: #6c757d;
          color: white;
        }

        .btn-danger {
          background-color: #dc3545;
          color: white;
        }

        .btn-sm {
          padding: 6px 12px;
          font-size: 12px;
        }
      `}</style>
    </div>
  );
};

export default DeliveryIntegration;
