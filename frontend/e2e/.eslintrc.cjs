/**
 * ESLint Configuration for E2E Tests
 */

module.exports = {
  env: {
    node: true,
    es2022: true,
  },
  extends: [
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  rules: {
    // インデント: 2スペース
    'indent': ['error', 2],

    // 行長: 120文字
    'max-len': ['warn', { code: 120, ignoreUrls: true, ignoreStrings: true }],

    // セミコロン必須
    'semi': ['error', 'always'],

    // シングルクォート優先
    'quotes': ['error', 'single', { avoidEscape: true }],

    // 未使用変数は警告
    'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],

    // console は許可（テストコード）
    'no-console': 'off',

    // await なし async は警告
    'require-await': 'warn',

    // 末尾カンマ
    'comma-dangle': ['error', 'always-multiline'],

    // オブジェクトのスペース
    'object-curly-spacing': ['error', 'always'],

    // 配列のスペース
    'array-bracket-spacing': ['error', 'never'],

    // アロー関数のスペース
    'arrow-spacing': ['error', { before: true, after: true }],

    // 比較演算子
    'eqeqeq': ['error', 'always'],

    // 変数宣言
    'no-var': 'error',
    'prefer-const': 'error',
  },
  globals: {
    // Playwright グローバル
    test: 'readonly',
    expect: 'readonly',
  },
};
