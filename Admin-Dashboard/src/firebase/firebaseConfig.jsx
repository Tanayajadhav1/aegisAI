// Import Firebase functions
import { initializeApp } from "firebase/app"
import { getAuth } from "firebase/auth"
import { getAnalytics } from "firebase/analytics"
import { getFirestore } from "firebase/firestore"

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAb5LKuQY6Pwm8DDaSX4L0x07I18IT0v7Q",
  authDomain: "aegis-ai-firewall.firebaseapp.com",
  projectId: "aegis-ai-firewall",
  storageBucket: "aegis-ai-firewall.firebasestorage.app",
  messagingSenderId: "942121719210",
  appId: "1:942121719210:web:2ecdd8bfb60fa2924907d3",
  measurementId: "G-00K4CDS3T5"
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)

// Firebase services
export const auth = getAuth(app)
export const db = getFirestore(app)

// Optional analytics
getAnalytics(app)