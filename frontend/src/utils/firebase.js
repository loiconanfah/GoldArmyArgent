// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAgxQbpF-I9U6RYwWTd0fLzxXeF8ab4Mqc",
    authDomain: "notificationfirebase-21d32.firebaseapp.com",
    projectId: "notificationfirebase-21d32",
    storageBucket: "notificationfirebase-21d32.firebasestorage.app",
    messagingSenderId: "845153829425",
    appId: "1:845153829425:web:1953590821443ba5358b10",
    measurementId: "G-502KTNWZSS"
};

// Initialize Firebase
export const firebaseApp = initializeApp(firebaseConfig);
export const analytics = typeof window !== 'undefined' ? getAnalytics(firebaseApp) : null;
