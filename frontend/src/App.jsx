import React, { useState, useEffect } from 'react';
import {
  AppRoot,
  SplitLayout, SplitCol,
  View,
  Panel, PanelHeader, Header,
  Switch, HorizontalScroll, IconButton,
  FormItem, Input, Button, Spacing,
  Group,
  SimpleCell, Cell,
  Avatar,
  Tabs, TabsItem,
  Tappable,
  Caption,
  Footnote,
  List, Link,
} from '@vkontakte/vkui';
import {
  Icon16Like, Icon16View,
  Icon24ChevronDown, Icon24ChevronUp,
  Icon28AddOutline, Icon24CheckCircleOn
} from '@vkontakte/icons';
import '@vkontakte/vkui/dist/vkui.css';

const App = () => {
  const API_URL = "http://127.0.0.1:8000";
  const [activePanel, setActivePanel] = useState('feed');
  const [selectedCategories, setSelectedCategories] = useState([0]);
  const [expandedTrend, setExpandedTrend] = useState(null);
  const [posts, setPosts] = useState([]);
  const [trends, setTrends] = useState([]);
  const [categories, setCategories] = useState([]);
  const [sources, setSources] = useState([]);
  const [newGroupUrl, setNewGroupUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [groups, setGroups] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sortBy, setSortBy] = useState('new');

  useEffect(() => {
    const fetchGroups = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`${API_URL}/groups`);
        if (response.ok) {
          const data = await response.json();
          setGroups(data);
        } else {
          console.error('Ошибка при загрузке групп');
        }
      } catch (error) {
        console.error('Ошибка сети:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchGroups();
  }, []);

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
        setCategories([{ id: 0, name: "Все" }, ...data]);
      } catch (error) {
        console.error("Ошибка при загрузке категорий:", error);
      }
    };

    fetchCategories();
  }, []);

  const fetchTrends = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/trends`);
      if (!response.ok) throw new Error('Ошибка при загрузке трендов');

      const data = await response.json();
      setTrends(data.trends || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchTrends(); }, []);

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

  const PostItem = ({ post }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const MAX_LENGTH = 250;
    const isLongText = post.text && post.text.length > MAX_LENGTH;

    return (
      <div style={{ borderBottom: '1px solid #e1e3e6', padding: '15px 12px' }}>
        {/* ШАПКА ПОСТА */}
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
          <Link href={post.group?.url} target="_blank" rel="noreferrer" style={{ marginRight: '12px' }}>
            <Avatar size={40} src={post.group?.avatar_path} />
          </Link>
          <div>
            <Link
              href={post.group?.url}
              target="_blank"
              rel="noreferrer"
              hoverMode="opacity"
              style={{
                fontWeight: 600,
                fontSize: '15px',
                color: 'var(--vkui--color_text_primary)',
                textDecoration: 'none',
                display: 'block'
              }}
            >
              {post.group?.title || post.group?.name}
            </Link>
            <div style={{ color: '#818c99', fontSize: '13px' }}>
              {new Date(post.posted_at).toLocaleDateString()}
            </div>
          </div>
        </div>

        {/* ТЕКСТ ПОСТА */}
        <div style={{ textAlign: 'left', marginBottom: '8px', whiteSpace: 'pre-wrap', fontSize: '15px' }}>
          {isLongText && !isExpanded
            ? `${post.text.substring(0, MAX_LENGTH)}...`
            : post.text
          }

          {isLongText && (
            <span
              onClick={() => setIsExpanded(!isExpanded)}
              style={{ color: '#2d73bc', cursor: 'pointer', fontWeight: '500', marginLeft: '5px' }}
            >
              {isExpanded ? ' Свернуть' : ' Показать полностью'}
            </span>
          )}
        </div>

        {/* ТЭГИ КАТЕГОРИИ */}
        <div style={{ display: 'flex', gap: '4px', marginBottom: '8px', flexWrap: 'wrap' }}>
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

        {/* КАРТИНКИ */}
        {post.images && post.images.length > 0 && (
          <div style={{
            display: 'grid',
            gap: '4px',
            gridTemplateColumns: post.images.length === 1 ? '1fr' : '1fr 1fr',
            marginBottom: '12px',
            borderRadius: '8px',
            overflow: 'hidden'
          }}>
            {post.images.map((imgUrl, index) => (
              <img key={index} src={imgUrl} alt="" style={{ width: '100%', height: '200px', objectFit: 'cover' }} />
            ))}
          </div>
        )}

        {/* ФУТЕР ПОСТА */}
        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#818c99', fontSize: '13px', marginTop: '12px' }}>
          <div style={{ display: 'flex', gap: '12px' }}>
            <span>❤️ {post.likes_count}</span>
            <span>👀 {post.views_count}</span>
          </div>
          {post.er && <span>ER: {post.er.toFixed(2)}%</span>}
        </div>
      </div>
    );
  };


  const TrendPostCard = ({ post }) => {
    const [isFullText, setIsFullText] = useState(false);
    const formattedDate = new Date(post.date).toLocaleString('ru-RU', {
      day: 'numeric',
      month: 'long',
      hour: '2-digit',
      minute: '2-digit'
    });
    const goToGroup = (e) => {
      e.stopPropagation();
      if (post.group?.url) {
        window.open(post.group.url, '_blank');
      }
    };

    return (
      <div style={{
        background: 'var(--vkui--color_background_content)',
        borderRadius: '10px',
        marginBottom: '8px',
        border: '1px solid var(--vkui--color_separator_primary)'
      }}>
        <SimpleCell
          before={
            <Tappable onClick={goToGroup} style={{ borderRadius: '50%' }}>
              <Avatar
                size={32}
                src={post.group?.avatar_path}
                fallbackCharacter={post.group?.name?.[0]}
              />
            </Tappable>
          }
          description={formattedDate}
        >
          <span
            onClick={goToGroup}
            style={{ fontWeight: 600, cursor: 'pointer', color: 'var(--vkui--color_text_primary)' }}
          >
            {post.group?.name || 'Источник'}
          </span>
        </SimpleCell>


        <div style={{ padding: '0 16px 12px 16px' }}>
          <Footnote
            onClick={() => setIsFullText(!isFullText)}
            style={{
              cursor: 'pointer',
              display: '-webkit-box',
              WebkitLineClamp: isFullText ? 'unset' : 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              lineHeight: '18px',
              whiteSpace: 'pre-wrap',
              color: 'var(--vkui--color_text_primary)'
            }}
          >
            {post.text}
          </Footnote>

          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: '10px',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', gap: '12px' }}>
              <Caption style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--vkui--color_text_secondary)' }}>
                <Icon16Like width={14} /> 0
              </Caption>
              <Caption style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--vkui--color_text_secondary)' }}>
                <Icon16View width={14} /> 0
              </Caption>
            </div>

            <Caption weight="2" style={{ color: 'var(--vkui--color_accent_blue)' }}>
              ER: {(post.er * 100).toFixed(4)}%
            </Caption>
          </div>
        </div>
      </div>
    );
  };

  const TrendsPanel = ({ id }) => {
    const [expandedTrend, setExpandedTrend] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    return (
      <Panel id={id}>
        <PanelHeader>Город Говорит</PanelHeader>

        {loading && <Spinner size="large" style={{ marginTop: 20 }} />}

        {error && (
          <Placeholder icon={<Icon56ErrorOutline fill="var(--vkui--color_icon_critical)" />} header="Ошибка">
            {error}
          </Placeholder>
        )}
        {!loading && !error && (
          <Group>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', padding: '8px' }}>
              {trends.map((trend) => (
                <React.Fragment key={trend.id}>
                  {/* Карточка тренда */}
                  <Tappable onClick={() => setExpandedTrend(expandedTrend === trend.id ? null : trend.id)}>
                    <b>{trend.name}</b>
                    {/* ... остальная разметка тренда ... */}
                  </Tappable>

                  {expandedTrend === trend.id && (
                    <div style={{ gridColumn: '1 / -1', padding: '8px 0' }}>
                      {trend.posts.map(post => (
                        <TrendPostCard key={post.id} post={post} />
                      ))}
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </Group>
        )}
      </Panel>
    );
  };

  const toggleItem = (id, list, setList, key) => {
    const newList = list.includes(id)
      ? list.filter(item => item !== id)
      : [...list, id];
    setList(newList);
    localStorage.setItem(key, JSON.stringify(newList));
  };

  const handleAddGroup = async () => {
    if (!groupUrl) return;

    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/groups/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: newGroupUrl }),
      });

      if (response.ok) {
        setNewGroupUrl('');
        console.log("Группа успешно добавлена");
      }
    } catch (error) {
      console.error("Ошибка при добавлении группы:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) return <div>Загрузка...</div>;

  return (
    <AppRoot>
      <SplitLayout header={<PanelHeader />}>
        <SplitCol>
          <View activePanel={activePanel}>

            <Panel id="feed">
              <PanelHeader>Город Говорит</PanelHeader>
              {headerTabs}
              {categoryFilters}
              <Group>
                {posts.length > 0 ? (
                  posts.map(post => (
                    <PostItem key={post.id} post={post} />
                  ))
                ) : (
                  <div style={{ padding: '40px', textAlign: 'center', color: '#818c99' }}>
                    Постов пока нет
                  </div>
                )}
              </Group>
            </Panel>


            <Panel id="trends">
              <PanelHeader>Город Говорит</PanelHeader>
              {headerTabs}
              {categoryFilters}
              <Group>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '8px',
                  padding: '8px'
                }}>
                  {trends.map((trend) => {
                    const isExpanded = expandedTrend === trend.id;

                    return (
                      <React.Fragment key={trend.id}>
                        {/* Карточка тренда */}
                        <Tappable
                          onClick={() => setExpandedTrend(isExpanded ? null : trend.id)}
                          style={{
                            background: 'var(--vkui--color_background_secondary)',
                            padding: '16px',
                            borderRadius: '12px',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            textAlign: 'center',
                            border: isExpanded ? '1px solid var(--vkui--color_accent_blue)' : 'none'
                          }}
                        >
                          <b style={{ fontSize: '14px', lineHeight: '18px' }}>{trend.name}</b>

                          <Caption level="2" style={{ color: 'var(--vkui--color_text_secondary)', marginTop: '4px' }}>
                            Постов: {trend.posts_count}
                          </Caption>

                          <Caption level="2" weight="2" style={{ color: 'var(--vkui--color_accent_blue)', marginTop: '2px' }}>
                            ER: {(trend.er * 100).toFixed(4)}%
                          </Caption>

                          <div style={{ marginTop: 4 }}>
                            {isExpanded ? <Icon24ChevronUp fill="gray" width={20} /> : <Icon24ChevronDown fill="gray" width={20} />}
                          </div>
                        </Tappable>

                        {/* Список постов под трендом */}
                        {isExpanded && (
                          <div style={{ gridColumn: '1 / -1', padding: '8px 0' }}>
                            {trend.posts.map((post) => (
                              <TrendPostCard key={post.id} post={post} />
                            ))}
                          </div>
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </Group>
            </Panel>

            <Panel id="settings">
              <PanelHeader>Настройки</PanelHeader>
              {headerTabs}

              <Group header={<Header mode="primary">Источники</Header>}>

                {/* Горизонтальный список аватарок */}
                {groups.length > 0 && (
                  <HorizontalScroll showArrows getScrollToLeft={(i) => i - 120} getScrollToRight={(i) => i + 120}>
                    <div style={{ display: 'flex', padding: '10px 0' }}>
                      {groups.map((group) => (
                        <div
                          key={group.id}
                          style={{
                            flexShrink: 0,
                            width: 80,
                            textAlign: 'center',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            gap: 4,
                            cursor: 'pointer'
                          }}
                        >
                          <Avatar size={48} src={group.avatar_path} alt={group.title} />
                          <div
                            style={{
                              fontSize: 12,
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              width: '100%',
                              padding: '0 4px',
                              color: 'var(--vkui--color_text_secondary)'
                            }}
                          >
                            {group.title}
                          </div>
                        </div>
                      ))}
                    </div>
                  </HorizontalScroll>
                )}

                <form onSubmit={(e) => { e.preventDefault(); handleAddGroup(); }}>
                  <FormItem
                    top="Добавить новую группу"
                    bottom="Вставьте ссылку, например: https://vk.com"
                  >
                    <Input
                      type="url"
                      placeholder="https://vk.com..."
                      value={newGroupUrl}
                      onChange={(e) => setNewGroupUrl(e.target.value)}
                      disabled={isSubmitting}
                    />
                  </FormItem>

                  <FormItem>
                    <Button
                      size="l"
                      stretched
                      type="submit"
                      loading={isSubmitting}
                      disabled={!newGroupUrl.trim()}
                    >
                      Добавить группу
                    </Button>
                  </FormItem>
                </form>
              </Group>
            </Panel>

          </View>
        </SplitCol>
      </SplitLayout>
    </AppRoot>
  );
};

export default App;

