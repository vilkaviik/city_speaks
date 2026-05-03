import React, { useState, useEffect } from 'react';
import {
  AppRoot,
  SplitLayout,
  SplitCol,
  View,
  Panel,
  PanelHeader,
  Group,
  SimpleCell,
  Avatar,
  Tabs,
  TabsItem,
  Tappable,
  Caption,
  Footnote,
  HorizontalScroll
} from '@vkontakte/vkui';
import {
  Icon16Like,
  Icon16View,
  Icon24ChevronDown,
  Icon24ChevronUp
} from '@vkontakte/icons';
import '@vkontakte/vkui/dist/vkui.css';

const App = () => {
  const API_URL = "http://127.0.0.1:8000";
  const [activePanel, setActivePanel] = useState('feed');
  const [selectedCategories, setSelectedCategories] = useState([0]);
  const [expandedTrend, setExpandedTrend] = useState(null);

  const [posts, setPosts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams();

        selectedCategories.forEach(id => {
          if (id !== 0) {
            params.append('category_ids', id);
          }
        });

        const response = await fetch(`${API_URL}/posts?${params.toString()}`);
        const data = await response.json();
        setPosts(data);
      } catch (error) {
        console.error("Ошибка при загрузке постов:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, [selectedCategories]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch(`${API_URL}/categories`);
        const data = await response.json();
        console.log("Данные из БД:", data);
        setCategories([{ id: 0, name: "Все" }, ...data]);
      } catch (error) {
        console.error("Ошибка при загрузке категорий:", error);
      }
    };

    fetchCategories();
  }, []);


  const toggleCategory = (id) => {
    setSelectedCategories((prev) => {
      if (id === 0) {
        return [0];
      }

      let next = prev.filter(itemId => itemId !== 0);

      if (next.includes(id)) {
        next = next.filter(itemId => itemId !== id);
      } else {

        next = [...next, id];
      }
      return next.length === 0 ? [0] : next;
    });
  };


  const [trendsData] = useState([
    {
      id: 'holiday',
      name: "# Праздник",
      likes: "2.4K",
      views: "150K",
      er: "4.2%",
      posts: [
        { id: 101, author: "Марина", text: "Как украсить дом к празднику?", likes: 45, views: 1200, er: "1.5%" },
        { id: 102, author: "Декор-Блог", text: "Топ 10 идей для гирлянд.", likes: 89, views: 3000, er: "2.8%" }
      ]
    },
    {
      id: 'kitchen',
      name: "# Кухня",
      likes: "1.8K",
      views: "98K",
      er: "3.5%",
      posts: [
        { id: 201, author: "Шеф", text: "Рецепт идеального омлета за 5 минут.", likes: 230, views: 15000, er: "5.1%" }
      ]
    }
  ]);

  const headerTabs = (
    <Tabs>
      <TabsItem selected={activePanel === 'feed'} onClick={() => setActivePanel('feed')}>Лента</TabsItem>
      <TabsItem selected={activePanel === 'trends'} onClick={() => setActivePanel('trends')}>Тренды</TabsItem>
      <TabsItem selected={activePanel === 'settings'} onClick={() => setActivePanel('settings')}>Настройки</TabsItem>
    </Tabs>
  );

  const categoryFilters = (
    <Group mode="plain">
      <HorizontalScroll showArrows getScrollToLeft={(i) => i - 40} getScrollToRight={(i) => i + 40}>
        <div style={{ display: 'flex', gap: '8px', padding: '8px 12px' }}>
          {categories.map((cat) => {
            const isSelected = selectedCategories.includes(cat.id);
            return (
              <Tappable
                key={cat.id}
                onClick={() => toggleCategory(cat.id)}
                style={{
                  padding: '6px 16px',
                  borderRadius: '16px',
                  fontSize: '14px',
                  backgroundColor: isSelected
                    ? 'var(--vkui--color_background_accent)'
                    : 'var(--vkui--color_background_secondary)',
                  color: isSelected
                    ? 'white'
                    : 'var(--vkui--color_text_primary)',
                  transition: '0.2s'
                }}
              >
                {cat.name}
              </Tappable>
            );
          })}
        </div>
      </HorizontalScroll>
    </Group>
  );

  if (loading) return <div>Загрузка...</div>;

  return (
    <AppRoot>
      <SplitLayout header={<PanelHeader />}>
        <SplitCol>
          <View activePanel={activePanel}>
            <Panel id="feed">
              <PanelHeader>Главная</PanelHeader>
              {headerTabs}
              {categoryFilters}
              <Group>
                {/* 1. Если посты есть — выводим их */}
                {posts.length > 0 ? (
                  posts.map(post => (
                    <section key={post.id} style={{ padding: '12px', borderBottom: '1px solid #ebedf0' }}>
                      <div style={{ marginBottom: '8px', whiteSpace: 'pre-wrap' }}>{post.text}</div>

                      <div style={{ display: 'flex', gap: '4px', marginBottom: '8px' }}>
                        {/* Обрати внимание: если industry это объект, а не массив, map не сработает */}
                        {Array.isArray(post.industry) ? post.industry.map(ind => (
                          <span key={ind.id} style={{ fontSize: '12px', color: '#818c99', background: '#f2f3f5', padding: '2px 6px', borderRadius: '4px' }}>
                            #{ind.name}
                          </span>
                        )) : post.industry && (
                          <span style={{ fontSize: '12px', color: '#818c99', background: '#f2f3f5', padding: '2px 6px', borderRadius: '4px' }}>
                            #{post.industry.name}
                          </span>
                        )}
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#818c99', fontSize: '13px' }}>
                        <div>❤️ {post.likes_count}  👀 {post.views_count}</div>
                        <div>{new Date(post.posted_at).toLocaleDateString()}</div>
                      </div>
                    </section>
                  ))
                ) : (
                  /* 2. Если постов нет и загрузка завершена — выводим заглушку */
                  !loading && (
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      padding: '40px 20px',
                      color: '#818c99'
                    }}>
                      <span style={{ fontSize: '48px', marginBottom: '12px' }}>🏜️</span>
                      <div style={{ fontSize: '16px', fontWeight: '500', color: 'var(--vkui--color_text_primary)' }}>
                        Постов пока нет
                      </div>
                      <div style={{ fontSize: '14px', marginTop: '4px' }}>
                        Попробуйте выбрать другую категорию
                      </div>
                    </div>
                  )
                )}
              </Group>
            </Panel>

            <Panel id="trends">
              <PanelHeader>Поиск</PanelHeader>
              {headerTabs}
              {categoryFilters}
              <Group>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', padding: '8px' }}>
                  {trendsData.map((trend) => (
                    <React.Fragment key={trend.id}>
                      {/* Карточка тренда */}
                      <Tappable
                        onClick={() => setExpandedTrend(expandedTrend === trend.id ? null : trend.id)}
                        style={{
                          background: 'var(--vkui--color_background_secondary)',
                          padding: '16px',
                          borderRadius: '12px',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          border: expandedTrend === trend.id ? '1px solid var(--vkui--color_accent_blue)' : 'none'
                        }}
                      >
                        <b style={{ fontSize: '16px' }}>{trend.name}</b>
                        <Caption level="2" style={{ color: 'var(--vkui--color_text_secondary)', marginTop: '4px', display: 'flex', gap: '6px' }}>
                          <span style={{ display: 'flex', alignItems: 'center' }}><Icon16Like width={12} />{trend.likes}</span>
                          <span style={{ display: 'flex', alignItems: 'center' }}><Icon16View width={12} />{trend.views}</span>
                        </Caption>
                        <Caption level="2" weight="2" style={{ color: 'var(--vkui--color_accent_blue)', marginTop: '2px' }}>ER: {trend.er}</Caption>
                        {expandedTrend === trend.id ? <Icon24ChevronUp fill="gray" /> : <Icon24ChevronDown fill="gray" />}
                      </Tappable>

                      {/* Список постов под трендом */}
                      {expandedTrend === trend.id && (
                        <div style={{ gridColumn: '1 / -1', padding: '8px 0' }}>
                          {trend.posts.map(post => (
                            <div key={post.id} style={{ background: 'var(--vkui--color_background_content)', borderRadius: '10px', marginBottom: '8px', border: '1px solid var(--vkui--color_separator_primary)' }}>
                              <SimpleCell before={<Avatar size={28} />}>{post.author}</SimpleCell>
                              <div style={{ padding: '0 16px 12px 16px' }}>
                                <Footnote>{post.text}</Footnote>
                                <div style={{ display: 'flex', gap: '12px', marginTop: '8px', color: 'var(--vkui--color_text_secondary)' }}>
                                  <Caption style={{ display: 'flex', alignItems: 'center', gap: '2px' }}><Icon16Like />{post.likes}</Caption>
                                  <Caption style={{ display: 'flex', alignItems: 'center', gap: '2px' }}><Icon16View />{post.views}</Caption>
                                  <Caption>ER: {post.er}</Caption>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </Group>
            </Panel>

            <Panel id="settings">
              <PanelHeader>Параметры</PanelHeader>
              {headerTabs}
              <Group>
                <SimpleCell before={<Avatar />}>Пользователь</SimpleCell>
              </Group>
            </Panel>

          </View>
        </SplitCol>
      </SplitLayout>
    </AppRoot>
  );
};

export default App;

