import React, { useState, useEffect } from 'react';
import {
  AppRoot,
  SplitLayout, SplitCol, Snackbar, SimpleCell, Slider,
  View, Div,
  Panel, PanelHeader, Header, PanelHeaderBack,
  Switch, HorizontalScroll, IconButton,
  FormItem, Input, Button, Spacing, Subhead, ButtonGroup,
  Group, FormLayoutGroup,
  Cell, Caption, CardGrid, ContentCard,
  Avatar, SegmentedControl,
  Tabs, TabsItem, Tappable, Textarea, Select, DateInput,
  Footnote, Footer, Checkbox,
  List, Link, InfoRow, Card, Title, Text as VKUIText
} from '@vkontakte/vkui';
import {
  Icon16Like, Icon16View, Icon24CancelOutline,
  Icon24ChevronDown, Icon24ChevronUp, Icon24RecentOutline, Icon24ReplayOutline,
  Icon28AddOutline, Icon24CheckCircleOn, Icon28CheckCircleOutline,
  Icon28ErrorCircleOutline, Icon28ServicesOutline
} from '@vkontakte/icons';
import '@vkontakte/vkui/dist/vkui.css';

const App = () => {
  const API_URL = "https://vilkaviik-city-speaks-d987.twc1.net";
  const [activePanel, setActivePanel] = useState('feed');
  const [snackbar, setSnackbar] = useState(null);

  // Состояния данных
  const [posts, setPosts] = useState([]);
  const [groups, setGroups] = useState([]);
  const [newGroupUrl, setNewGroupUrl] = useState('');
  const [trends, setTrends] = useState([]);
  const [selectedTimespan, setSelectedTimespan] = useState('24h');
  const [expandedTrend, setExpandedTrend] = useState(null);
  const [categories, setCategories] = useState([]);
  const [sources, setSources] = useState([]);

  // Состояния для фильтров
  const [sortBy, setSortBy] = useState('new');
  const [selectedTrendCategories, setSelectedTrendCategories] = useState([0]);
  const [selectedCategories, setSelectedCategories] = useState([0]);
  const [selectedGroupIds, setSelectedGroupIds] = useState(() => {
    const saved = localStorage.getItem('selectedGroupIds');
    return saved ? JSON.parse(saved) : [];
  });

  const [loading, setLoading] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const [isFullListOpen, setIsFullListOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  const [industries, setIndustries] = useState([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [categoryName, setCategoryName] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [categoryDescription, setCategoryDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedCategoryIds, setSelectedCategoryIds] = useState([]);
  const [isEditMode, setIsEditMode] = useState(false);

  const [prompt, setPrompt] = useState("");
  const [temp, setTemp] = useState(0.3);
  const [isDownloading, setDownloading] = useState(false);

  const [statusFilter, setStatusFilter] = useState('active');
  const FIELD_DESCRIPTIONS = {
    // Посты
    text: { label: "Текст поста", desc: "Оригинальный текст публикации" },
    cleaned_text: { label: "Очищенный текст", desc: "Текст без ссылок, эмодзи и спецсимволов" },
    normalized_text: { label: "Нормализованный текст", desc: "Текст, приведенный к начальной форме (лемматизация)" },
    embedding: { label: "Эмбеддинг", desc: "Векторное представление текста (256 чисел)" },
    er: { label: "ER", desc: "Коэффициент вовлеченности (Engagement Rate)" },
    posted_at: { label: "Дата публикации", desc: "Когда пост был опубликован в источнике" },

    // Тренды
    name: { label: "Название тренда", desc: "Ключевое слово или фраза тренда" },
    timespan: { label: "Период", desc: "Временной охват тренда (например, 24h)" },
    is_active: { label: "Активен", desc: "Статус актуальности тренда на данный момент" },

    // Группы
    subscribers: { label: "Подписчики", desc: "Количество участников сообщества" },
    vk_id: { label: "VK ID", desc: "Уникальный идентификатор сообщества ВКонтакте" }
  };

  const TABLES_CONFIG = {
    trends: ['id', 'name', 'er', 'timespan', 'industry_id', 'is_active', 'discovered_at'],
    posts: ['id', 'text', 'cleaned_text', 'normalized_text', 'embedding', 'likes_count', 'views_count', 'er', 'url', 'posted_at'],
    industries: ['id', 'name', 'description'],
    groups: ['id', 'vk_id', 'title', 'screen_name', 'subscribers']
  };

  const saveSettings = () => {
    console.log("Сохранено:", { prompt, temp });
  };

  const resetSettings = () => {
    // Вызов эндпоинта /admin/reset_prompt
    // После успеха обновляем стейт:
    // setPrompt(defaultPrompt); setTemp(0.3);
  };

  const toggleGroup = (groupId) => {
    const nextIds = selectedGroupIds.includes(groupId)
      ? selectedGroupIds.filter(id => id !== groupId)
      : [...selectedGroupIds, groupId];

    setSelectedGroupIds(nextIds);
    localStorage.setItem('selectedGroupIds', JSON.stringify(nextIds));
  };

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await fetch(`${API_URL}/groups`);
        const data = await response.json();
        setGroups(data);

        const saved = localStorage.getItem('selectedGroupIds');
        if (!saved && data.length > 0) {
          const allIds = data.map(g => g.id);
          setSelectedGroupIds(allIds);
          localStorage.setItem('selectedGroupIds', JSON.stringify(allIds));
        }
      } catch (e) { console.error(e); }
    };
    fetchGroups();
  }, []);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams();
        params.append('sort', sortBy);

        selectedCategories.forEach(id => {
          if (id !== 0) params.append('category_ids', id);
        });

        selectedGroupIds.forEach(id => {
          params.append('group_ids', id);
        });

        const response = await fetch(`${API_URL}/posts?${params.toString()}`);
        const data = await response.json();
        setPosts(data);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, [selectedCategories, sortBy, selectedGroupIds]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch(`${API_URL}/categories`);
        const data = await response.json();
        setCategories(data);
        setSelectedCategoryIds(data.map(c => c.id));
      } catch (error) {
        console.error("Ошибка при загрузке категорий:", error);
      }
    };
    fetchCategories();
  }, []);

  const toggleCategoryUser = (id) => {
    setSelectedCategoryIds(prev =>
      prev.includes(id)
        ? prev.filter(itemId => itemId !== id)
        : [...prev, id]
    );
  };

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams();
        params.append('timespan', selectedTimespan);
        selectedTrendCategories.forEach(id => {
          if (id !== 0) params.append('category_ids', id);
        });

        const response = await fetch(`${API_URL}/trends?${params.toString()}`);
        if (!response.ok) throw new Error('Ошибка при загрузке трендов');

        const data = await response.json();
        setTrends(data.trends || []);
      } catch (err) {
        console.error("Ошибка при загрузке трендов:", err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchTrends();
  }, [selectedTrendCategories, selectedTimespan]);

  const toggleCategory = (id, setter) => {
    setter((prev) => {
      if (id === 0) return [0];
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

  const sortingTabs = (
    <Tabs mode="secondary" style={{ marginBottom: '8px' }}>
      <TabsItem
        selected={sortBy === 'new'}
        onClick={() => setSortBy('new')}
      >
        Новые
      </TabsItem>
      <TabsItem
        selected={sortBy === 'top'}
        onClick={() => setSortBy('top')}
      >
        Популярные
      </TabsItem>
    </Tabs>
  );

  const renderCategoryFilters = (selectedList, onToggle) => (
    <Group mode="plain">
      <HorizontalScroll showArrows getScrollToLeft={(i) => i - 40} getScrollToRight={(i) => i + 40}>
        <div style={{ display: 'flex', gap: '8px', padding: '8px 12px' }}>
          {categories.map((cat) => {
            const isSelected = selectedList.includes(cat.id);
            return (
              <Tappable
                key={cat.id}
                onClick={() => onToggle(cat.id)}
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
          <div style={{ textAlign: 'left' }}>
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
                display: 'block',
                textAlign: 'left'
              }}
            >
              {post.group?.title || post.group?.name}
            </Link>
            <div style={{ fontSize: '13px' }}>
              <a
                href={post.url}
                target="_blank"
                rel="noreferrer"
                style={{ color: '#818c99', textDecoration: 'none' }}
              >
                {new Date(post.posted_at).toLocaleString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric'
                })}
              </a>
            </div>
          </div>
        </div>

        {/* ТЕКСТ ПОСТА */}
        <div style={{ textAlign: 'left', marginBottom: '8px', whiteSpace: 'pre-wrap', fontSize: '15px' }}>
          {isLongText && !isExpanded
            ? `${post.text.substring(0, MAX_LENGTH)}...`
            : post.text
          }
          <a
            href={post.url}
            target="_blank"
            rel="noreferrer"
            style={{ color: 'inherit', textDecoration: 'none' }}
          >
            {isLongText && !isExpanded
              ? `${post.text.substring(0, MAX_LENGTH)}...`
              : post.text
            }
          </a>

          {isLongText && (
            <span
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
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
              {ind.name}
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
            <span>Нравится {post.likes_count}</span>
            <span>Просмотрено {post.views_count}</span>
          </div>
          {post.er && <span>Вовлеченность: {(post.er * 100).toFixed(4)}%</span>}
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
            alignItems: 'flex-end'
          }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {/* ЛАЙКИ И ПРОСМОТРЫ */}
              <div style={{ display: 'flex', gap: '12px' }}>
                <Caption style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--vkui--color_text_secondary)' }}>
                  <Icon16Like width={14} /> {post.likes_count || 0}
                </Caption>
                <Caption style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--vkui--color_text_secondary)' }}>
                  <Icon16View width={14} /> {post.views_count || 0}
                </Caption>
              </div>

              {/* ДАТА И ВРЕМЯ */}
              <div style={{ color: '#818c99', fontSize: '12px' }}>
                {formattedDate}
              </div>
            </div>

            <Caption weight="2" style={{ color: 'var(--vkui--color_accent_blue)', textAlign: 'right' }}>
              <div>Вовлеченность:</div>
              <div>{(post.er * 100).toFixed(4)}%</div>
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
                  <Tappable onClick={() => setExpandedTrend(expandedTrend === trend.id ? null : trend.id)}>
                    <b>{trend.name}</b>
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

  const openSuccessSnackbar = () => {
    if (snackbar) return;

    setSnackbar(
      <Snackbar
        duration={4000}
        onClose={() => setSnackbar(null)}
        before={<Icon28CheckCircleOutline fill="var(--vkui--color_icon_positive)" />}
        action="Закрыть"
      >
        Группа успешно добавлена
      </Snackbar>
    );
  };

  const openErrorSnackbar = (text = "Произошла ошибка при добавлении") => {
    setSnackbar(
      <Snackbar
        duration={4000}
        onClose={() => setSnackbar(null)}
        before={<Icon28ErrorCircleOutline fill="var(--vkui--color_icon_negative)" />}
        action="Закрыть"
      >
        {text}
      </Snackbar>
    );
  };

  const handleAddGroup = async () => {
    if (!newGroupUrl) return;

    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/groups/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: newGroupUrl }),
      });

      if (response.ok) {
        setNewGroupUrl('');
        openSuccessSnackbar(); // Вызов успеха
      } else {
        openErrorSnackbar("Сервер отклонил запрос. Проверьте ссылку."); // Вызов ошибки сервера
      }
    } catch (error) {
      openErrorSnackbar("Ошибка сети. Проверьте соединение."); // Вызов сетевой ошибки
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectAllGroups = () => {
    const allIds = groups.map(g => g.id);
    setSelectedGroupIds(allIds);
    localStorage.setItem('selectedGroupIds', JSON.stringify(allIds));
  };

  const deselectAllGroups = () => {
    setSelectedGroupIds([]);
    localStorage.setItem('selectedGroupIds', JSON.stringify([]));
  };

  const handleAddCategory = async () => {
    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/industries/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: categoryName,
          description: categoryDescription
        })
      });

      if (response.ok) {
        const newCategory = await response.json();
        setCategories(prev => [...prev, newCategory]); // Добавляем в список
        setCategoryName(''); // Очищаем поля
        setCategoryDescription('');
      }
    } catch (error) {
      console.error("Ошибка при добавлении:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const openEditModeCategory = () => {
    setIsEditMode(true);
    setActivePanel('edit_categories_panel');
  };

  const renderLLMSettings = () => {
    const defaultPrompt = "Ты — аналитик новостей. Твоя задача: прочитать несколько текстов и придумать ОДНО общее краткое название темы (до 5-7 слов). Пиши только название, без лишних слов.";
    return (
      <Group header={<Header mode="primary">Нейросети</Header>}>
        <FormItem
          top="Системный промпт"
          bottom={prompt === "" ? "Сейчас используется промпт по умолчанию" : "Используется ваш кастомный промпт"}
        >
          <Textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            // Отображается серым цветом, когда поле пустое
            placeholder={defaultPrompt}
            style={{ minHeight: 120 }}
          />
        </FormItem>

        {prompt !== "" && (
          <Div style={{ paddingTop: 0, paddingBottom: 0 }}>
            <Button
              mode="tertiary"
              size="s"
              onClick={() => setPrompt("")}
              style={{ marginLeft: -12 }}
            >
              Использовать по умолчанию
            </Button>
          </Div>
        )}

        <FormItem top={`Температура генерации: ${temp}`}>
          <Slider
            step={0.1}
            min={0}
            max={1}
            value={temp}
            onChange={(v) => setTemp(v)}
          />
          <Div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
            <Subhead weight="3" style={{ color: 'var(--vkui--color_text_secondary)' }}>Точность</Subhead>
            <Subhead weight="3" style={{ color: 'var(--vkui--color_text_secondary)' }}>Креативность</Subhead>
          </Div>
        </FormItem>

        <Spacing size={16} />

        <Div>
          <ButtonGroup mode="horizontal" gap="m" stretched>
            <Button
              size="l"
              stretched
              before={<Icon24RecentOutline />}
              onClick={saveSettings}
            >
              Сохранить
            </Button>
            <Button
              size="l"
              mode="secondary"
              appearance="negative"
              before={<Icon24ReplayOutline />}
              onClick={resetSettings}
            >
              Сброс
            </Button>
          </ButtonGroup>
        </Div>
      </Group>
    );
  };


  const renderExportBlock = () => {
    const API_BASE = "https://vilkaviik-city-speaks-d987.twc1.net";

    const handleDownload = (format) => {
      window.open(`${API_BASE}/export/trends/${format}`, '_blank');
    };

    return (
      <Group header={<Header mode="primary">Экспорт и отчеты</Header>}>
        <Div>
          <ButtonGroup mode="vertical" gap="m" stretched>
            <Button size="l" mode="outline" onClick={() => handleDownload('json')}>
              Экспорт в JSON
            </Button>
            {/* остальные кнопки */}
          </ButtonGroup>
        </Div>
      </Group>
    );
  };

  const ExportDataSection = () => {
    const [table, setTable] = useState('trends');
    const [selectedFields, setSelectedFields] = useState(TABLES_CONFIG['trends']);
    const [format, setFormat] = useState('json');
    const [dateFrom, setDateFrom] = useState(null);
    const [dateTo, setDateTo] = useState(null);

    const handleTableChange = (e) => {
      const val = e.target.value;
      setTable(val);
      setSelectedFields(TABLES_CONFIG[val]);
    };

    const toggleField = (field) => {
      setSelectedFields(prev =>
        prev.includes(field) ? prev.filter(f => f !== field) : [...prev, field]
      );
    };

    const handleDownload = () => {
      const params = new URLSearchParams();
      selectedFields.forEach(f => params.append('fields', f));
      params.append('format', format);
      if (dateFrom) params.append('date_from', dateFrom.toISOString());
      if (dateTo) params.append('date_to', dateTo.toISOString());

      const url = `${API_URL}/export/${table}?${params.toString()}`;
      window.open(url, '_blank');
    };

    return (
      <Group
        header={<Header mode="primary">Экспорт данных из БД</Header>}
        description="Выберите таблицу, нужные поля и формат файла для выгрузки"
      >
        <form onSubmit={(e) => e.preventDefault()}>

          <div style={{ display: 'flex', gap: '12px', padding: '0 16px' }}>
            <FormItem label="Таблица" style={{ flexGrow: 1, padding: '12px 0' }}>
              <Select
                value={table}
                onChange={handleTableChange}
                options={Object.keys(TABLES_CONFIG).map(t => ({ label: t, value: t }))}
              />
            </FormItem>

            <FormItem label="Формат" style={{ width: 120 }}>
              <Select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                options={[
                  { label: 'JSON', value: 'json' },
                  { label: 'SQL', value: 'sql' }
                ]}
              />
            </FormItem>
          </div>

          <div style={{ display: 'flex', gap: '12px', padding: '0 16px' }}>
            <FormItem label="Дата от" style={{ flex: 1, padding: '12px 0' }}>
              <DateInput value={dateFrom} onChange={setDateFrom} />
            </FormItem>
            <FormItem label="Дата до" style={{ flex: 1, padding: '12px 0' }}>
              <DateInput value={dateTo} onChange={setDateTo} />
            </FormItem>
          </div>

          <FormItem label="Выберите поля для выгрузки">
            <Div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', 
              gap: '16px',
              padding: 0
            }}>
              {TABLES_CONFIG[table].map(field => {
                const info = FIELD_DESCRIPTIONS[field] || { label: field, desc: "" };
                return (
                  <Checkbox
                    key={field}
                    checked={selectedFields.includes(field)}
                    onChange={() => toggleField(field)}
                    style={{
                      alignItems: 'center', 
                      display: 'flex',
                      padding: '4px 0'
                    }}
                  >
                    <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column' }}>
                      <span style={{ fontWeight: 500, fontSize: '15px', lineHeight: '20px' }}>
                        {info.label}
                      </span>
                      {info.desc && (
                        <span style={{
                          color: 'var(--vkui--color_text_secondary)',
                          fontSize: '13px',
                          lineHeight: '16px',
                          marginTop: '2px'
                        }}>
                          {info.desc}
                        </span>
                      )}
                    </div>
                  </Checkbox>
                );
              })}

            </Div>
          </FormItem>

          <Spacing size={16} />

          <FormItem>
            <Button
              size="l"
              appearance="accent"
              stretched
              onClick={handleDownload}
              disabled={selectedFields.length === 0}
            >
              Сформировать и скачать
            </Button>
          </FormItem>
        </form>
      </Group>
    );
  };

  if (loading) return <div>Загрузка...</div>;

  return (
    <AppRoot>
      <SplitLayout header={<PanelHeader />}
        popout={snackbar}
      >
        <SplitCol>
          <View activePanel={activePanel}>

            <Panel id="feed">
              <PanelHeader>Город Говорит</PanelHeader>
              {headerTabs}
              {renderCategoryFilters(selectedCategories, (id) => toggleCategory(id, setSelectedCategories))}
              {sortingTabs}

              <Group>
                {posts.length > 0 ? (
                  posts.map(post => (
                    <PostItem key={post.id} post={post} />
                  ))
                ) : (
                  !loading && (
                    <div style={{ padding: '40px', textAlign: 'center', color: '#818c99' }}>
                      Постов пока нет
                    </div>
                  )
                )}

                {loading && <Spinner size="medium" style={{ margin: '20px 0' }} />}
              </Group>
            </Panel>

            <Panel id="trends">
              <PanelHeader>Город Говорит</PanelHeader>
              {headerTabs}
              {renderCategoryFilters(selectedTrendCategories, (id) => toggleCategory(id, setSelectedTrendCategories))}
              <Tabs mode="secondary">
                <TabsItem
                  selected={selectedTimespan === '24h'}
                  onClick={() => setSelectedTimespan('24h')}
                >
                  24 часа
                </TabsItem>
                <TabsItem
                  selected={selectedTimespan === '3d'}
                  onClick={() => setSelectedTimespan('3d')}
                >
                  3 дня
                </TabsItem>
                <TabsItem
                  selected={selectedTimespan === '7d'}
                  onClick={() => setSelectedTimespan('7d')}
                >
                  Неделя
                </TabsItem>
              </Tabs>
              <Group style={{ padding: '0 16px 12px' }}>
                <SegmentedControl
                  size="m"
                  value={statusFilter}
                  onChange={(value) => setStatusFilter(value)}
                  options={[
                    { label: 'Активные', value: 'active' },
                    { label: 'Архив', value: 'archived' },
                  ]}
                />
              </Group>
              <Group>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '8px',
                  padding: '8px'
                }}>
                  {trends
                    .filter(trend => {
                      const matchesStatus = statusFilter === 'active' ? trend.is_active : !trend.is_active;
                      return matchesStatus;
                    })
                    .map((trend) => {
                      const isExpanded = expandedTrend === trend.id;
                      const industryName = trend.industry && trend.industry.length > 0
                        ? trend.industry[0].name
                        : null;

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
                              opacity: trend.is_active ? 1 : 0.6,
                              border: isExpanded ? '1px solid var(--vkui--color_accent_blue)' : 'none'
                            }}
                          >
                            {industryName && (
                              <Caption
                                level="2"
                                style={{ color: 'var(--vkui--color_text_tertiary)', marginBottom: '4px', textTransform: 'uppercase', fontSize: '10px' }}
                              >
                                {industryName}
                              </Caption>
                            )}

                            <b style={{ fontSize: '14px', lineHeight: '18px' }}>{trend.name}</b>

                            <Caption level="2" style={{ color: 'var(--vkui--color_text_secondary)', marginTop: '4px' }}>
                              Постов: {trend.posts_count}
                            </Caption>

                            <Caption level="2" weight="2" style={{ color: 'var(--vkui--color_accent_blue)', marginTop: '2px' }}>
                              Вовлеченность: {(trend.er * 100).toFixed(4)}%
                            </Caption>

                            <div style={{ marginTop: 4 }}>
                              {isExpanded ? <Icon24ChevronUp fill="gray" width={20} /> : <Icon24ChevronDown fill="gray" width={20} />}
                            </div>
                          </Tappable>

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
              <PanelHeader>Город Говорит</PanelHeader>
              {headerTabs}

              <Group header={
                <Header
                  mode="primary"
                  after={
                    <span
                      onClick={() => setActivePanel('all_groups_grid')}
                      style={{
                        color: 'var(--vkui--color_text_link)',
                        cursor: 'pointer',
                        fontSize: '14px'
                      }}
                    >
                      Все
                    </span>
                  }
                >
                  Источники
                </Header>
              }>

                {/* Горизонтальный список аватарок */}
                {groups.length > 0 && (
                  <HorizontalScroll showArrows getScrollToLeft={(i) => i - 120} getScrollToRight={(i) => i + 120}>
                    <div style={{ display: 'flex', padding: '10px 0' }}>
                      {groups.slice()
                        .sort((a, b) => a.title.localeCompare(b.title))
                        .map((group) => (
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

              <Group
                header={
                  <Header
                    mode="primary"
                    after={
                      <span
                        onClick={() => setActivePanel('edit_categories_panel')}
                        style={{
                          color: 'var(--vkui--color_text_link)',
                          cursor: 'pointer',
                          fontSize: '14px'
                        }}
                      >
                        Редактировать
                      </span>
                    }
                  >
                    Категории
                  </Header>

                }
              >
                {(isExpanded ? categories : categories.slice(0, 3)).map((item) => (
                  <SimpleCell
                    key={item.id}
                    before={<Icon28ServicesOutline fill="var(--vkui--color_icon_accent)" width={24} height={24} />}
                    subtitle={item.description}
                    // Если категория выключена, делаем её полупрозрачной
                    style={{ opacity: selectedCategoryIds.includes(item.id) ? 1 : 0.5 }}
                    multiline
                  >
                    <span style={{ fontSize: 14, fontWeight: 500 }}>{item.name}</span>
                  </SimpleCell>

                ))}

                {isEditMode && (
                  <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    background: 'var(--vkui--color_background_content)',
                    zIndex: 100, padding: '10px'
                  }}>
                    <Group
                      header={
                        <Header
                          mode="secondary"
                          aside={<Button onClick={() => setIsEditMode(false)}>Готово</Button>}
                        >
                          НАСТРОЙКА ВИДИМОСТИ
                        </Header>
                      }
                    >
                      {categories.map((item) => (
                        <SimpleCell
                          key={item.id}
                          before={
                            <Checkbox
                              checked={selectedCategoryIds.includes(item.id)}
                              onChange={() => toggleCategory(item.id)}
                            />
                          }
                          onClick={() => toggleCategory(item.id)}
                          after={
                            <IconButton onClick={(e) => { e.stopPropagation(); handleDeleteCategory(item.id); }}>
                              <Icon24CancelOutline />
                            </IconButton>
                          }
                        >
                          {item.name}
                        </SimpleCell>
                      ))}
                    </Group>
                  </div>
                )}

                {categories.length > 3 && (
                  <Cell
                    centered
                    onClick={() => setIsExpanded(!isExpanded)}
                    style={{ color: 'var(--vkui--color_text_accent)' }}
                  >
                    {isExpanded ? 'Свернуть' : `Показать все`}
                  </Cell>
                )}

                <form onSubmit={(e) => { e.preventDefault(); handleAddCategory(); }}>
                  <Header mode="secondary">Добавить новую категорию</Header>

                  <FormItem
                    top="Название категории"
                    bottom="Короткое название для фильтра (например: Технологии)"
                  >
                    <Input
                      type="text"
                      placeholder="Введите название..."
                      value={categoryName}
                      onChange={(e) => setCategoryName(e.target.value)}
                      disabled={isSubmitting}
                    />
                  </FormItem>

                  <FormItem
                    top="Описание"
                    bottom="Расскажите, какие посты попадут в эту категорию"
                  >
                    <Textarea
                      placeholder="Описание категории..."
                      value={categoryDescription}
                      onChange={(e) => setCategoryDescription(e.target.value)}
                      disabled={isSubmitting}
                    />
                  </FormItem>

                  <FormItem>
                    <Button
                      size="l"
                      stretched
                      type="submit"
                      loading={isSubmitting}
                      disabled={!categoryName.trim() || !categoryDescription.trim()}
                    >
                      Добавить категорию
                    </Button>
                  </FormItem>
                </form>

                {categories.length === 0 && (
                  <Footer>Категории пока не добавлены</Footer>
                )}
              </Group>
              <ExportDataSection />
            </Panel>

            <Panel id="all_groups_grid">
              <PanelHeader before={<PanelHeaderBack onClick={() => setActivePanel('settings')} />}>
                Все источники
              </PanelHeader>

              <Group>
                <div style={{ padding: '10px 16px' }}>
                  <Button
                    size="m"
                    mode={isEditing ? "primary" : "outline"}
                    stretched
                    onClick={() => setIsEditing(!isEditing)}
                  >
                    {isEditing ? 'Готово' : 'Редактировать список'}
                  </Button>

                  {isEditing && (
                    <div style={{
                      display: 'flex',
                      justifyContent: 'center',
                      gap: 8,
                      marginTop: 12
                    }}>
                      <Button mode="tertiary" size="s" onClick={selectAllGroups}>
                        Выбрать все
                      </Button>
                      <Button mode="tertiary" size="s" appearance="negative" onClick={deselectAllGroups}>
                        Отменить выбор
                      </Button>
                    </div>
                  )}
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: '16px 8px',
                  padding: '10px'
                }}>
                  {groups.sort((a, b) => a.title.localeCompare(b.title)).map((group) => {
                    const isSelected = selectedGroupIds.includes(group.id);
                    return (
                      <div
                        key={group.id}
                        onClick={() => isEditing && toggleGroup(group.id)}
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          position: 'relative',
                          opacity: !isSelected && !isEditing ? 0.5 : 1,
                          transition: 'opacity 0.2s ease'
                        }}
                      >
                        <div style={{ position: 'relative' }}>
                          <Avatar size={64} src={group.avatar_path} />
                          {isSelected && (
                            <div style={{
                              position: 'absolute', bottom: 0, right: 0,
                              backgroundColor: 'var(--vkui--color_background_accent)',
                              borderRadius: '50%', width: 22, height: 22,
                              border: '2px solid var(--vkui--color_background_content)',
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              color: 'white', fontSize: '12px'
                            }}>✓</div>
                          )}
                        </div>
                        <div style={{ fontSize: 12, marginTop: 6, textAlign: 'center' }}>
                          {group.title}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </Group>
            </Panel>

            <Panel id="edit_categories_panel">
              <PanelHeader
                before={<PanelHeaderBack onClick={() => setActivePanel('settings')} />}
                after={
                  <Button mode="tertiary" onClick={() => setActivePanel('settings')}>
                    Готово
                  </Button>
                }
              >
                Настройка видимости
              </PanelHeader>

              <Group>
                <div style={{ display: 'flex', justifyContent: 'center', gap: 8, padding: '12px' }}>
                  <Button mode="tertiary" size="s" onClick={selectAllGroups}>
                    Выбрать все
                  </Button>
                  <Button mode="tertiary" size="s" appearance="negative" onClick={deselectAllGroups}>
                    Снять выделение
                  </Button>
                </div>

                {/* Список категорий */}
                {categories.map((item) => (
                  <SimpleCell
                    key={item.id}
                    before={
                      <Checkbox
                        checked={selectedCategoryIds.includes(item.id)}
                        onChange={() => toggleCategory(item.id)}
                      />
                    }
                    onClick={() => toggleCategory(item.id)}
                    after={
                      <IconButton
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteCategory(item.id);
                        }}
                        aria-label="Удалить категорию"
                      >
                        <Icon24CancelOutline />
                      </IconButton>
                    }
                  >
                    {item.name}
                  </SimpleCell>
                ))}
              </Group>
            </Panel>

          </View>
        </SplitCol>
      </SplitLayout>
    </AppRoot>
  );
};

export default App;

