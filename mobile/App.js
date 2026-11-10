import { useState } from 'react';
import { View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { colors } from './src/theme';
import Welcome from './src/screens/Welcome';
import SignUp from './src/screens/SignUp';
import LogIn from './src/screens/LogIn';
import Home from './src/screens/Home';
import Stops from './src/screens/Stops';
import Tickets from './src/screens/Tickets';
import Payment from './src/screens/Payment';
import Confirmation from './src/screens/Confirmation';
import PlanTrip from './src/screens/PlanTrip';
import Results from './src/screens/Results';
import Updates from './src/screens/Updates';
import More from './src/screens/More';
import Accessibility from './src/screens/Accessibility';
import History from './src/screens/History';
import Admin from './src/screens/Admin';
import Reports from './src/screens/Reports';
import CreateAlert from './src/screens/CreateAlert';
import Emergency from './src/screens/Emergency';

const screens = {
  welcome: Welcome, signup: SignUp, login: LogIn,
  home: Home, stops: Stops, tickets: Tickets, payment: Payment, confirmation: Confirmation,
  plan: PlanTrip, results: Results, updates: Updates, more: More, accessibility: Accessibility,
  history: History, admin: Admin, reports: Reports, createalert: CreateAlert,
  emergency: Emergency,
};
const publicScreens = ['welcome', 'signup', 'login'];

export default function App() {
  const [screen, setScreen] = useState('welcome');
  const [session, setSession] = useState(null); // { token, user } after logging in
  const [notice, setNotice] = useState('');
  const [params, setParams] = useState({});     // data handed from one screen to the next

  const go = (name, message = '', p = {}) => {
    setNotice(message);
    setParams(p);
    setScreen(name);
  };

  const shown = !publicScreens.includes(screen) && !session ? 'welcome' : screen;
  const Screen = screens[shown] || Welcome;

  return (
    <View style={{ flex: 1, alignItems: 'center', backgroundColor: '#a9c7d6' }}>
      <View style={{ flex: 1, width: '100%', maxWidth: 402, backgroundColor: colors.sky }}>
        <Screen go={go} session={session} setSession={setSession} notice={notice} params={params} />
      </View>
      <StatusBar style="auto" />
    </View>
  );
}