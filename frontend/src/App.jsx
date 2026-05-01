import React, { useState, useEffect } from 'react';
import bridge from '@vkontakte/vk-bridge';
import { 
  AppRoot, 
  SplitLayout, 
  SplitCol, 
  View, 
  Panel, 
  PanelHeader, 
  Header, 
  Group, 
  SimpleCell, 
  Avatar, 
  Spinner, Tabs, TabsItem, 
  ContentCard 
} from '@vkontakte/vkui';
import '@vkontakte/vkui/dist/vkui.css';

const App = () => {
  const [activePanel, setActivePanel] = useState('feed'); // текущий экран
  const [user, setUser] = useState({ /* твои моки */ });

  // Верхние кнопки
  const headerTabs = (
    <Tabs>
      <TabsItem
        selected={activePanel === 'feed'}
        onClick={() => setActivePanel('feed')}
      >
        Лента
      </TabsItem>
      <TabsItem
        selected={activePanel === 'trends'}
        onClick={() => setActivePanel('trends')}
      >
        Тренды
      </TabsItem>
      <TabsItem
        selected={activePanel === 'settings'}
        onClick={() => setActivePanel('settings')}
      >
        Настройки
      </TabsItem>
    </Tabs>
  );

  const [posts, setPosts] = useState([
  {
    id: 1,
    author: "Александра",
    text: "Сегодня запустила фронтенд на VKUI! FastAPI на очереди. 🚀",
    image: "https://picsum.photos",
    date: "5 мин. назад"
  },
  {
    id: 2,
    author: "Бэкенд-разработчик",
    text: "Написал первый эндпоинт на FastAPI. Работает быстрее молнии! ⚡",
    image: "https://picsum.photos",
    date: "1 час назад"
  },
  {
    id: 3,
    author: "Дизайнер",
    text: "Тренды в мини-приложениях ВК выглядят очень нативно.",
    date: "3 часа назад"
  }
]);

  return (
    <AppRoot>
      <SplitLayout header={<PanelHeader />}>
        <SplitCol>
          <View activePanel={activePanel}>
            
            {/* ЛЕНТА */}
            <Panel id="feed">
              <PanelHeader>Главная</PanelHeader>
              {headerTabs}
              <Group>
  {posts.map((post) => (
    <div key={post.id} style={{ 
      padding: '12px', 
      borderBottom: '1px solid var(--vkui--color_separator_primary_alpha)' 
    }}>
      {/* Шапка поста: Аватарка и Имя */}
      <SimpleCell
        style={{ padding: 0 }}
        before={<Avatar size={40} src={post.image || ""} />}
        subtitle={post.date}
        disabled
      >
        <span style={{ fontWeight: 600 }}>{post.author}</span>
      </SimpleCell>

      {/* Текст поста */}
      <div style={{ padding: '4px 0 8px 52px', fontSize: '15px', lineHeight: '20px' }}>
        {post.text}
      </div>

      {/* Картинка поста (если есть) */}
      {post.image && (
        <div style={{ paddingLeft: '52px' }}>
          <img 
            src={post.image} 
            alt="post" 
            style={{ width: '100%', borderRadius: '10px', display: 'block' }} 
          />
        </div>
      )}
    </div>
  ))}
</Group>


            </Panel>

            {/* ТРЕНДЫ */}
            <Panel id="trends">
              <PanelHeader>Поиск</PanelHeader>
              {headerTabs} {/* Кнопки сверху */}
              <Group>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', padding: '8px' }}>
                   <div style={{ background: 'var(--vkui--color_background_secondary)', padding: '24px', borderRadius: '12px', textAlign: 'center' }}>
                     <b># Праздник</b>
                   </div>
                   <div style={{ background: 'var(--vkui--color_background_secondary)', padding: '24px', borderRadius: '12px', textAlign: 'center' }}>
                     <b># Кухня</b>
                   </div>
                </div>
              </Group>
            </Panel>

            {/* НАСТРОЙКИ */}
            <Panel id="settings">
              <PanelHeader>Параметры</PanelHeader>
              {headerTabs} {/* Кнопки сверху */}
              <Group>
                <SimpleCell before={<Avatar src={user?.photo_200} />}>
                  {user?.first_name} {user?.last_name}
                </SimpleCell>
              </Group>
            </Panel>

          </View>
        </SplitCol>
      </SplitLayout>
    </AppRoot>
  );
};


export default App;
