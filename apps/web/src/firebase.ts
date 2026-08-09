import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'

const firebaseConfig = {
  apiKey: 'AIzaSyAoJyINTiV9d0UUL8FdVBAZrBwv4kHPORk',
  authDomain: 'annex-3aa64.firebaseapp.com',
  projectId: 'annex-3aa64',
  storageBucket: 'annex-3aa64.firebasestorage.app',
  messagingSenderId: '654328152054',
  appId: '1:654328152054:web:32b675bf31ccebd83091d7',
  measurementId: 'G-NWFDSH24WR',
}

export const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)
