/**
 * Google Actions Webhook Handler
 * Personal Recipe Intelligence Google Assistant アクション
 */

const express = require('express');
const bodyParser = require('body-parser');
const { dialogflow, SimpleResponse, BasicCard, Suggestions } = require('actions-on-google');
const axios = require('axios');

// API エンドポイント設定
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api/v1';

// Dialogflow アプリ作成
const app = dialogflow({
  debug: true
});

/**
 * Welcome Intent
 */
app.intent('Default Welcome Intent', (conv) => {
  conv.ask(new SimpleResponse({
    speech: 'パーソナルレシピインテリジェンスへようこそ。レシピ名を言うか、レシピを検索してください。',
    text: 'レシピ名を言うか、検索してください'
  }));

  conv.ask(new Suggestions(['カレーのレシピ', '材料を読んで', '次の手順']));
});

/**
 * Get Recipe Intent
 */
app.intent('com.pri.intent.GET_RECIPE', async (conv, { recipeName }) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/recipes/search`, {
      params: { q: recipeName }
    });

    if (response.data.data.length > 0) {
      const recipe = response.data.data[0];

      // セッションデータに保存
      conv.data.currentRecipe = recipe;
      conv.data.currentStepIndex = 0;

      conv.ask(new SimpleResponse({
        speech: `${recipe.title}のレシピを開きました。材料を読む、または次の手順、と言ってください。`,
        text: `${recipe.title}を開きました`
      }));

      if (recipe.image_url) {
        conv.ask(new BasicCard({
          title: recipe.title,
          text: recipe.description || 'レシピの詳細',
          image: {
            url: recipe.image_url,
            accessibilityText: recipe.title
          }
        }));
      }

      conv.ask(new Suggestions(['材料を読んで', '次の手順', '全部読んで']));
    } else {
      conv.ask(new SimpleResponse({
        speech: `${recipeName}のレシピが見つかりませんでした。別のレシピ名を言ってください。`,
        text: 'レシピが見つかりませんでした'
      }));

      conv.ask(new Suggestions(['レシピ検索', '他のレシピ']));
    }
  } catch (error) {
    console.error('API Error:', error);
    conv.ask('レシピの取得中にエラーが発生しました。');
  }
});

/**
 * Read Ingredients Intent
 */
app.intent('com.pri.intent.READ_INGREDIENTS', (conv) => {
  const recipe = conv.data.currentRecipe;

  if (!recipe) {
    conv.ask('レシピが設定されていません。レシピ名を言ってください。');
    conv.ask(new Suggestions(['カレーのレシピ', 'レシピ検索']));
    return;
  }

  let speech = '材料は、';
  recipe.ingredients.forEach((ingredient, index) => {
    speech += `${ingredient.name}が${ingredient.amount}`;
    if (index < recipe.ingredients.length - 1) {
      speech += '、';
    }
  });
  speech += '、以上です。';

  conv.ask(new SimpleResponse({
    speech: speech,
    text: '材料リスト'
  }));

  conv.ask(new Suggestions(['次の手順', '最初から', '全部読んで']));
});

/**
 * Next Step Intent
 */
app.intent('com.pri.intent.NEXT_STEP', (conv) => {
  const recipe = conv.data.currentRecipe;

  if (!recipe) {
    conv.ask('レシピが設定されていません。');
    return;
  }

  let stepIndex = conv.data.currentStepIndex || 0;

  if (stepIndex < recipe.steps.length) {
    const step = recipe.steps[stepIndex];

    conv.ask(new SimpleResponse({
      speech: `手順${stepIndex + 1}、${step}`,
      text: `手順${stepIndex + 1}`
    }));

    conv.data.currentStepIndex = stepIndex + 1;

    if (stepIndex + 1 < recipe.steps.length) {
      conv.ask(new Suggestions(['次の手順', '前の手順', 'もう一度']));
    } else {
      conv.ask(new Suggestions(['前の手順', '最初から', '材料を読んで']));
    }
  } else {
    conv.ask('最後の手順です。お疲れ様でした。');
    conv.ask(new Suggestions(['最初から', '材料を読んで']));
  }
});

/**
 * Previous Step Intent
 */
app.intent('com.pri.intent.PREVIOUS_STEP', (conv) => {
  const recipe = conv.data.currentRecipe;

  if (!recipe) {
    conv.ask('レシピが設定されていません。');
    return;
  }

  let stepIndex = conv.data.currentStepIndex || 0;

  if (stepIndex > 0) {
    stepIndex--;
    const step = recipe.steps[stepIndex];

    conv.ask(new SimpleResponse({
      speech: `手順${stepIndex + 1}、${step}`,
      text: `手順${stepIndex + 1}`
    }));

    conv.data.currentStepIndex = stepIndex;
    conv.ask(new Suggestions(['次の手順', '前の手順', 'もう一度']));
  } else {
    conv.ask('最初の手順です。');
    conv.ask(new Suggestions(['次の手順', '材料を読んで']));
  }
});

/**
 * Repeat Step Intent
 */
app.intent('com.pri.intent.REPEAT_STEP', (conv) => {
  const recipe = conv.data.currentRecipe;

  if (!recipe) {
    conv.ask('レシピが設定されていません。');
    return;
  }

  const stepIndex = conv.data.currentStepIndex || 0;

  if (stepIndex > 0 && stepIndex <= recipe.steps.length) {
    const step = recipe.steps[stepIndex - 1];

    conv.ask(new SimpleResponse({
      speech: `手順${stepIndex}、${step}`,
      text: `手順${stepIndex}`
    }));

    conv.ask(new Suggestions(['次の手順', '前の手順', 'もう一度']));
  } else {
    conv.ask('手順を開始してください。');
    conv.ask(new Suggestions(['次の手順', '材料を読んで']));
  }
});

/**
 * Start From Beginning Intent
 */
app.intent('com.pri.intent.START_FROM_BEGINNING', (conv) => {
  const recipe = conv.data.currentRecipe;

  if (!recipe) {
    conv.ask('レシピが設定されていません。');
    return;
  }

  conv.data.currentStepIndex = 0;

  conv.ask(new SimpleResponse({
    speech: `${recipe.title}の最初から始めます。次の手順、と言ってください。`,
    text: '最初から開始'
  }));

  conv.ask(new Suggestions(['次の手順', '材料を読んで', '全部読んで']));
});

/**
 * Set Timer Intent
 */
app.intent('com.pri.intent.SET_TIMER', (conv, { duration }) => {
  conv.ask(new SimpleResponse({
    speech: `${duration}のタイマーを設定しました。`,
    text: `タイマー設定: ${duration}`
  }));

  conv.ask(new Suggestions(['次の手順', '前の手順']));
});

/**
 * Search Recipe Intent
 */
app.intent('com.pri.intent.SEARCH_RECIPE', async (conv, { keyword }) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/recipes/search`, {
      params: { q: keyword }
    });

    if (response.data.data.length > 0) {
      const recipes = response.data.data.slice(0, 3);
      let speech = `${keyword}で${recipes.length}件見つかりました。`;

      recipes.forEach((recipe, index) => {
        speech += `${index + 1}、${recipe.title}。`;
      });

      speech += '開きたいレシピ名を言ってください。';

      conv.ask(new SimpleResponse({
        speech: speech,
        text: `検索結果: ${recipes.length}件`
      }));

      const suggestions = recipes.slice(0, 3).map(r => r.title);
      conv.ask(new Suggestions(suggestions));
    } else {
      conv.ask(`${keyword}のレシピが見つかりませんでした。`);
    }
  } catch (error) {
    console.error('Search Error:', error);
    conv.ask('検索中にエラーが発生しました。');
  }
});

/**
 * Read All Intent
 */
app.intent('com.pri.intent.READ_ALL', (conv) => {
  const recipe = conv.data.currentRecipe;

  if (!recipe) {
    conv.ask('レシピが設定されていません。');
    return;
  }

  let speech = `レシピ名は${recipe.title}です。`;

  if (recipe.ingredients && recipe.ingredients.length > 0) {
    speech += '材料は、';
    recipe.ingredients.forEach((ingredient, index) => {
      speech += `${ingredient.name}が${ingredient.amount}`;
      if (index < recipe.ingredients.length - 1) {
        speech += '、';
      }
    });
    speech += '。';
  }

  if (recipe.steps && recipe.steps.length > 0) {
    speech += '手順は、';
    recipe.steps.forEach((step, index) => {
      speech += `${index + 1}、${step}。`;
    });
  }

  conv.ask(new SimpleResponse({
    speech: speech,
    text: recipe.title
  }));

  conv.ask(new Suggestions(['次の手順', '材料を読んで', '最初から']));
});

/**
 * Go To Step Intent
 */
app.intent('com.pri.intent.GO_TO_STEP', (conv, { stepNumber }) => {
  const recipe = conv.data.currentRecipe;

  if (!recipe) {
    conv.ask('レシピが設定されていません。');
    return;
  }

  const index = parseInt(stepNumber) - 1;

  if (index >= 0 && index < recipe.steps.length) {
    const step = recipe.steps[index];

    conv.ask(new SimpleResponse({
      speech: `手順${stepNumber}、${step}`,
      text: `手順${stepNumber}`
    }));

    conv.data.currentStepIndex = index + 1;
    conv.ask(new Suggestions(['次の手順', '前の手順', 'もう一度']));
  } else {
    conv.ask(`手順${stepNumber}は存在しません。`);
  }
});

// Express サーバー設定
const expressApp = express();
expressApp.use(bodyParser.json());

expressApp.post('/webhook', app);

const PORT = process.env.PORT || 3000;
expressApp.listen(PORT, () => {
  console.log(`Google Actions webhook listening on port ${PORT}`);
});

module.exports = expressApp;
