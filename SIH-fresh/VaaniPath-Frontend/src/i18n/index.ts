import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enIN from './locales/en-IN.json';
import hiIN from './locales/hi-IN.json';
import bnIN from './locales/bn-IN.json';
import mrIN from './locales/mr-IN.json';
import taIN from './locales/ta-IN.json';
import teIN from './locales/te-IN.json';
import guIN from './locales/gu-IN.json';
import knIN from './locales/kn-IN.json';
import mlIN from './locales/ml-IN.json';
import paIN from './locales/pa-IN.json';
import asIN from './locales/as-IN.json';
import brxIN from './locales/brx-IN.json';
import doiIN from './locales/doi-IN.json';
import ksIN from './locales/ks-IN.json';
import kokIN from './locales/kok-IN.json';
import maiIN from './locales/mai-IN.json';
import mniIN from './locales/mni-IN.json';
import neIN from './locales/ne-IN.json';
import orIN from './locales/or-IN.json';
import saIN from './locales/sa-IN.json';
import satIN from './locales/sat-IN.json';
import sdIN from './locales/sd-IN.json';
import urIN from './locales/ur-IN.json';

export const resources = {
    'en-IN': { translation: enIN },
    'hi-IN': { translation: hiIN },
    'bn-IN': { translation: bnIN },
    'mr-IN': { translation: mrIN },
    'ta-IN': { translation: taIN },
    'te-IN': { translation: teIN },
    'gu-IN': { translation: guIN },
    'kn-IN': { translation: knIN },
    'ml-IN': { translation: mlIN },
    'pa-IN': { translation: paIN },
    'as-IN': { translation: asIN },
    'brx-IN': { translation: brxIN },
    'doi-IN': { translation: doiIN },
    'ks-IN': { translation: ksIN },
    'kok-IN': { translation: kokIN },
    'mai-IN': { translation: maiIN },
    'mni-IN': { translation: mniIN },
    'ne-IN': { translation: neIN },
    'or-IN': { translation: orIN },
    'sa-IN': { translation: saIN },
    'sat-IN': { translation: satIN },
    'sd-IN': { translation: sdIN },
    'ur-IN': { translation: urIN },
} as const;

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources,
        fallbackLng: 'en-IN',
        interpolation: {
            escapeValue: false,
        },
        detection: {
            order: ['localStorage', 'navigator'],
            caches: ['localStorage'],
        },
    });

export default i18n;
