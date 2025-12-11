/**
 * Alexa Skill Lambda Handler
 * Personal Recipe Intelligence Alexa スキル
 */

const Alexa = require('ask-sdk-core');
const axios = require('axios');

// API エンドポイント設定
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * LaunchRequestHandler
 */
const LaunchRequestHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
  },
  handle(handlerInput) {
    const speakOutput = 'パーソナルレシピインテリジェンスへようこそ。レシピ名を言うか、レシピを検索してください。';

    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  }
};

/**
 * GetRecipeIntentHandler
 */
const GetRecipeIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && Alexa.getIntentName(handlerInput.requestEnvelope) === 'GetRecipeIntent';
  },
  async handle(handlerInput) {
    const recipeName = Alexa.getSlotValue(handlerInput.requestEnvelope, 'recipeName');

    try {
      const response = await axios.get(`${API_BASE_URL}/recipes/search`, {
        params: { q: recipeName }
      });

      if (response.data.data.length > 0) {
        const recipe = response.data.data[0];
        const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
        sessionAttributes.currentRecipe = recipe;
        sessionAttributes.currentStepIndex = 0;
        handlerInput.attributesManager.setSessionAttributes(sessionAttributes);

        const speakOutput = `${recipe.title}のレシピを開きました。材料を読む、または次の手順、と言ってください。`;

        return handlerInput.responseBuilder
          .speak(speakOutput)
          .reprompt('材料を読む、または次の手順、と言ってください。')
          .getResponse();
      } else {
        return handlerInput.responseBuilder
          .speak(`${recipeName}のレシピが見つかりませんでした。`)
          .reprompt('別のレシピ名を言ってください。')
          .getResponse();
      }
    } catch (error) {
      console.error('API Error:', error);
      return handlerInput.responseBuilder
        .speak('レシピの取得中にエラーが発生しました。')
        .getResponse();
    }
  }
};

/**
 * ReadIngredientsIntentHandler
 */
const ReadIngredientsIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ReadIngredientsIntent';
  },
  handle(handlerInput) {
    const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
    const recipe = sessionAttributes.currentRecipe;

    if (!recipe) {
      return handlerInput.responseBuilder
        .speak('レシピが設定されていません。レシピ名を言ってください。')
        .reprompt('レシピ名を言ってください。')
        .getResponse();
    }

    let speakOutput = '材料は、';
    recipe.ingredients.forEach((ingredient, index) => {
      speakOutput += `${ingredient.name}が${ingredient.amount}`;
      if (index < recipe.ingredients.length - 1) {
        speakOutput += '、';
      }
    });
    speakOutput += '、以上です。';

    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt('次の手順、と言ってください。')
      .getResponse();
  }
};

/**
 * NextStepIntentHandler
 */
const NextStepIntentHandler = {
  canHandle(handlerInput) {
    return (Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && Alexa.getIntentName(handlerInput.requestEnvelope) === 'NextStepIntent')
      || Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.NextIntent';
  },
  handle(handlerInput) {
    const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
    const recipe = sessionAttributes.currentRecipe;

    if (!recipe) {
      return handlerInput.responseBuilder
        .speak('レシピが設定されていません。')
        .getResponse();
    }

    let stepIndex = sessionAttributes.currentStepIndex || 0;

    if (stepIndex < recipe.steps.length) {
      const step = recipe.steps[stepIndex];
      const speakOutput = `手順${stepIndex + 1}、${step}`;

      sessionAttributes.currentStepIndex = stepIndex + 1;
      handlerInput.attributesManager.setSessionAttributes(sessionAttributes);

      return handlerInput.responseBuilder
        .speak(speakOutput)
        .reprompt('次の手順、または前の手順、と言ってください。')
        .getResponse();
    } else {
      return handlerInput.responseBuilder
        .speak('最後の手順です。お疲れ様でした。')
        .getResponse();
    }
  }
};

/**
 * PreviousStepIntentHandler
 */
const PreviousStepIntentHandler = {
  canHandle(handlerInput) {
    return (Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && Alexa.getIntentName(handlerInput.requestEnvelope) === 'PreviousStepIntent')
      || Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.PreviousIntent';
  },
  handle(handlerInput) {
    const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
    const recipe = sessionAttributes.currentRecipe;

    if (!recipe) {
      return handlerInput.responseBuilder
        .speak('レシピが設定されていません。')
        .getResponse();
    }

    let stepIndex = sessionAttributes.currentStepIndex || 0;

    if (stepIndex > 0) {
      stepIndex--;
      const step = recipe.steps[stepIndex];
      const speakOutput = `手順${stepIndex + 1}、${step}`;

      sessionAttributes.currentStepIndex = stepIndex;
      handlerInput.attributesManager.setSessionAttributes(sessionAttributes);

      return handlerInput.responseBuilder
        .speak(speakOutput)
        .reprompt('次の手順、または前の手順、と言ってください。')
        .getResponse();
    } else {
      return handlerInput.responseBuilder
        .speak('最初の手順です。')
        .getResponse();
    }
  }
};

/**
 * RepeatStepIntentHandler
 */
const RepeatStepIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && Alexa.getIntentName(handlerInput.requestEnvelope) === 'RepeatStepIntent';
  },
  handle(handlerInput) {
    const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
    const recipe = sessionAttributes.currentRecipe;

    if (!recipe) {
      return handlerInput.responseBuilder
        .speak('レシピが設定されていません。')
        .getResponse();
    }

    const stepIndex = sessionAttributes.currentStepIndex || 0;

    if (stepIndex > 0 && stepIndex <= recipe.steps.length) {
      const step = recipe.steps[stepIndex - 1];
      const speakOutput = `手順${stepIndex}、${step}`;

      return handlerInput.responseBuilder
        .speak(speakOutput)
        .reprompt('次の手順、または前の手順、と言ってください。')
        .getResponse();
    } else {
      return handlerInput.responseBuilder
        .speak('手順を開始してください。')
        .getResponse();
    }
  }
};

/**
 * SetTimerIntentHandler
 */
const SetTimerIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && Alexa.getIntentName(handlerInput.requestEnvelope) === 'SetTimerIntent';
  },
  handle(handlerInput) {
    const duration = Alexa.getSlotValue(handlerInput.requestEnvelope, 'duration');

    // タイマー設定のリクエスト（実際にはデバイスのタイマーAPIを使用）
    const speakOutput = `${duration}のタイマーを設定しました。`;

    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  }
};

/**
 * HelpIntentHandler
 */
const HelpIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.HelpIntent';
  },
  handle(handlerInput) {
    const speakOutput = 'レシピ名を言うか、材料を読んで、次の手順、などと言ってください。';

    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  }
};

/**
 * CancelAndStopIntentHandler
 */
const CancelAndStopIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.CancelIntent'
        || Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.StopIntent');
  },
  handle(handlerInput) {
    const speakOutput = 'またのご利用をお待ちしています。';

    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  }
};

/**
 * SessionEndedRequestHandler
 */
const SessionEndedRequestHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'SessionEndedRequest';
  },
  handle(handlerInput) {
    console.log(`Session ended: ${JSON.stringify(handlerInput.requestEnvelope)}`);
    return handlerInput.responseBuilder.getResponse();
  }
};

/**
 * ErrorHandler
 */
const ErrorHandler = {
  canHandle() {
    return true;
  },
  handle(handlerInput, error) {
    console.error(`Error handled: ${error.message}`);
    console.error(error);

    const speakOutput = 'エラーが発生しました。もう一度お試しください。';

    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  }
};

/**
 * Lambda Handler
 */
exports.handler = Alexa.SkillBuilders.custom()
  .addRequestHandlers(
    LaunchRequestHandler,
    GetRecipeIntentHandler,
    ReadIngredientsIntentHandler,
    NextStepIntentHandler,
    PreviousStepIntentHandler,
    RepeatStepIntentHandler,
    SetTimerIntentHandler,
    HelpIntentHandler,
    CancelAndStopIntentHandler,
    SessionEndedRequestHandler
  )
  .addErrorHandlers(ErrorHandler)
  .lambda();
