import { PageHeader } from "../components/ui/PageHeader";
import { MenuCard } from "../components/ui/MenuCard";
import { WelcomeSection } from "../components/ui/WelcomeSection";
import { useNavigate } from "react-router-dom";
import { useUserStore } from "../context/useUserStore";
import { UserRole } from "../constants/roles";
import statisticIcon from "../assets/icons/statistic-board-com.svg";
import usersIcon from "../assets/icons/users.svg";
import settingsIcon from "../assets/icons/settings.svg";
import shopIcon from "../assets/icons/shop.svg";

interface MenuCardData {
  path: string;
  label: string;
  description: string;
  icon: string;
  allowedRoles: UserRole[];
}

const menuCards: MenuCardData[] = [
  {
    path: "/stats",
    label: "Статистика",
    description: "Перегляд статистики замовлень",
    icon: statisticIcon,
    allowedRoles: [UserRole.MANAGER, UserRole.OWNER],
  },
  {
    path: "/staff",
    label: "Персонал",
    description: "Управління співробітниками",
    icon: usersIcon,
    allowedRoles: [UserRole.OWNER],
  },
  {
    path: "/shop-settings",
    label: "Налаштування магазину",
    description: "Адреса магазину та райони доставки",
    icon: shopIcon,
    allowedRoles: [UserRole.OWNER],
  },
  {
    path: "/settings",
    label: "Налаштування",
    description: "Налаштування додатку",
    icon: settingsIcon,
    allowedRoles: [UserRole.MANAGER, UserRole.OWNER],
  },
];

export const MainPage = () => {
  const navigate = useNavigate();
  const user = useUserStore((s) => s.user);

  const hasPermission = (card: MenuCardData): boolean => {
    return user ? card.allowedRoles.includes(user.role) : false;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <PageHeader title="Головна" />

      <div className="px-6 pb-24 pt-4">
        <WelcomeSection
          title="Вітаємо! 👋"
          subtitle="Оберіть розділ для швидкого доступу"
        />

        <div className="grid grid-cols-1 gap-4">
          {menuCards.map((card) => (
            <MenuCard
              key={card.path}
              label={card.label}
              description={card.description}
              icon={card.icon}
              onClick={() => navigate(card.path)}
              disabled={!hasPermission(card)}
            />
          ))}
        </div>

        <div className="h-4" />
      </div>
    </div>
  );
};
