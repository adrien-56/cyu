const {
  Client,
  GatewayIntentBits,
  EmbedBuilder,
  ButtonBuilder,
  ButtonStyle,
  ActionRowBuilder
} = require('discord.js');
const fs = require('fs');

/* ========== CONFIG ========== */

const TOKEN = 'MTQyMjMwMzU1MTA4NTg3MTE0Ng.GuIkaS.I-7xbGcowSIupExWlmjzdHNproVtLHoJBPhEZk';
const ADMIN_ROLE_ID = '1449754506060628172';
const LOG_CHANNEL_ID = '1449743458939048017';

/* ========== CLIENT ========== */

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

/* ========== DATA ========== */

const players = new Map(); 
// userId -> { rp, wins, losses }

const rankBadges = new Map(); 
// rankName -> emoji

/* ========== FILE PATHS ========== */

const PLAYERS_FILE = 'players.json';
const BADGES_FILE = 'badges.json';

/* ========== LOAD/SAVE FUNCTIONS ========== */

function loadPlayers() {
  if (fs.existsSync(PLAYERS_FILE)) {
    const data = JSON.parse(fs.readFileSync(PLAYERS_FILE, 'utf8'));
    for (const [id, p] of Object.entries(data)) {
      players.set(id, p);
    }
  }
}

function savePlayers() {
  const data = {};
  for (const [id, p] of players) {
    data[id] = p;
  }
  fs.writeFileSync(PLAYERS_FILE, JSON.stringify(data, null, 2));
}

function loadBadges() {
  if (fs.existsSync(BADGES_FILE)) {
    const data = JSON.parse(fs.readFileSync(BADGES_FILE, 'utf8'));
    for (const [rank, emoji] of Object.entries(data)) {
      rankBadges.set(rank, emoji);
    }
  }
}

function saveBadges() {
  const data = {};
  for (const [rank, emoji] of rankBadges) {
    data[rank] = emoji;
  }
  fs.writeFileSync(BADGES_FILE, JSON.stringify(data, null, 2));
}

/* ========== RANK SYSTEM ========== */

const RANKS = [
  { name: 'Bronze', rp: 0 },
  { name: 'Silver', rp: 15 },
  { name: 'Gold', rp: 25 },
  { name: 'Platinum', rp: 35 },
  { name: 'Diamond', rp: 45 },
  { name: 'Immortal', rp: 55 }
];

function getRank(rp) {
  let r = 'Bronze';
  for (const rank of RANKS) if (rp >= rank.rp) r = rank.name;
  return r;
}

function rankIndex(name) {
  return RANKS.findIndex(r => r.name === name);
}

function rpChange(winnerRank, loserRank) {
  const diff = rankIndex(winnerRank) - rankIndex(loserRank);
  if (diff === 0) return { win: 2, loss: -1 };
  if (diff < 0) return { win: 1.5, loss: -0.5 };
  return { win: 1, loss: -1.5 };
}

/* ========== UTIL ========== */

function initPlayer(id) {
  if (!players.has(id)) {
    players.set(id, { rp: 0, wins: 0, losses: 0 });
  }
}

function getLeaderboard(limit = 20) {
  return Array.from(players.entries())
    .map(([id, data]) => ({ id, ...data, rank: getRank(data.rp) }))
    .sort((a, b) => {
      if (b.rp !== a.rp) return b.rp - a.rp;
      const aTotal = a.wins + a.losses;
      const bTotal = b.wins + b.losses;
      const aWr = aTotal ? (a.wins / aTotal) : 0;
      const bWr = bTotal ? (b.wins / bTotal) : 0;
      return bWr - aWr;
    })
    .slice(0, limit);
}

async function createLeaderboardEmbed(leaderboard, page, totalPages) {
  const embed = new EmbedBuilder()
    .setColor(0xffd700)
    .setTitle('🏆 Pokétwo Ranked Leaderboard')
    .setDescription(`Top players by RP (Page ${page + 1}/${totalPages})`)
    .setTimestamp();

  const start = page * 10;
  const end = start + 10;
  const pagePlayers = leaderboard.slice(start, end);

  let description = '';
  for (let i = 0; i < pagePlayers.length; i++) {
    const player = pagePlayers[i];
    const user = await client.users.fetch(player.id).catch(() => null);
    const username = user ? user.username : 'Unknown';
    const badge = rankBadges.get(player.rank) || '⬜';
    const total = player.wins + player.losses;
    const wr = total ? ((player.wins / total) * 100).toFixed(1) : '0.0';
    description += `${start + i + 1}. ${badge} ${username} - RP: ${player.rp}, Wins: ${player.wins}, WR: ${wr}%\n`;
  }
  embed.setDescription(description || 'No players on this page.');

  return embed;
}

function createLeaderboardButtons(page, totalPages) {
  const row = new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId(`lb_prev_${page}`)
      .setLabel('Previous')
      .setEmoji('⬅️')
      .setStyle(ButtonStyle.Primary)
      .setDisabled(page === 0),
    new ButtonBuilder()
      .setCustomId(`lb_next_${page}`)
      .setLabel('Next')
      .setEmoji('➡️')
      .setStyle(ButtonStyle.Primary)
      .setDisabled(page === totalPages - 1)
  );
  return row;
}

/* ========== COMMANDS ========== */

client.on('messageCreate', async message => {
  if (message.author.bot) return;
  if (!message.content.startsWith('>')) return;

  const args = message.content.slice(1).trim().split(/\s+/);
  const cmd = args.shift().toLowerCase();

  /* ===== HELP ===== */
  if (cmd === 'help') {
    const embed = new EmbedBuilder()
      .setColor(0x5865f2)
      .setTitle('📘 Pokétwo Ranked PvP — Help')
      .setDescription('Community-managed ranked PvP system')
      .addFields(
        {
          name: '🎮 Player Commands',
          value:
            '`>log @user`\n`>profile [@user]` or `>pf [@user]`\n`>lb`\n`>help`'
        },
        {
          name: '🛠 Admin Commands',
          value:
            '`>setbadge <Rank> <Emoji>`\n`>addrp @user <amount>`\n`>removerp @user <amount>`'
        },
      )
      .setTimestamp();

    const row = new ActionRowBuilder().addComponents(
      new ButtonBuilder()
        .setCustomId('help_close')
        .setLabel('Close')
        .setEmoji('🗑️')
        .setStyle(ButtonStyle.Secondary)
    );

    return message.channel.send({ embeds: [embed], components: [row] });
  }

  /* ===== SET BADGE ===== */
  if (cmd === 'setbadge') {
    if (!message.member.roles.cache.has(ADMIN_ROLE_ID))
      return message.reply('Admins only.');

    const rank = args.shift();
    const emoji = args.join(' ');
    if (!rank || !emoji)
      return message.reply('Usage: >setbadge <Rank> <Emoji>');

    const valid = RANKS.find(r => r.name.toLowerCase() === rank.toLowerCase());
    if (!valid) return message.reply('Invalid rank.');

    rankBadges.set(valid.name, emoji);
    saveBadges();
    return message.channel.send(`✅ ${valid.name} badge set to ${emoji}`);
  }

  /* ===== ADD RP ===== */
  if (cmd === 'addrp') {
    if (!message.member.roles.cache.has(ADMIN_ROLE_ID))
      return message.reply('Admins only.');

    const user = message.mentions.users.first();
    if (!user) return message.reply('Mention a user.');

    const amount = parseFloat(args[0]);
    if (isNaN(amount) || amount <= 0)
      return message.reply('Provide a positive number for RP to add.');

    initPlayer(user.id);
    const p = players.get(user.id);
    p.rp += amount;
    savePlayers();

    const log = message.guild.channels.cache.get(LOG_CHANNEL_ID);
    if (log) {
      const embed = new EmbedBuilder()
        .setTitle('Pokétwo RP Adjustment Log')
        .setColor(0x00ff00)
        .addFields(
          { name: 'Admin', value: `<@${message.author.id}>`, inline: true },
          { name: 'Player', value: `<@${user.id}>`, inline: true },
          { name: 'Action', value: `Added ${amount} RP`, inline: true },
          { name: 'New RP', value: `${p.rp}`, inline: true }
        )
        .setTimestamp();
      log.send({ embeds: [embed] });
    }

    return message.channel.send(`✅ Added ${amount} RP to <@${user.id}>. New RP: ${p.rp}`);
  }

  /* ===== REMOVE RP ===== */
  if (cmd === 'removerp') {
    if (!message.member.roles.cache.has(ADMIN_ROLE_ID))
      return message.reply('Admins only.');

    const user = message.mentions.users.first();
    if (!user) return message.reply('Mention a user.');

    const amount = parseFloat(args[0]);
    if (isNaN(amount) || amount <= 0)
      return message.reply('Provide a positive number for RP to remove.');

    initPlayer(user.id);
    const p = players.get(user.id);
    p.rp = Math.max(0, p.rp - amount);
    savePlayers();

    const log = message.guild.channels.cache.get(LOG_CHANNEL_ID);
    if (log) {
      const embed = new EmbedBuilder()
        .setTitle('Pokétwo RP Adjustment Log')
        .setColor(0xff0000)
        .addFields(
          { name: 'Admin', value: `<@${message.author.id}>`, inline: true },
          { name: 'Player', value: `<@${user.id}>`, inline: true },
          { name: 'Action', value: `Removed ${amount} RP`, inline: true },
          { name: 'New RP', value: `${p.rp}`, inline: true }
        )
        .setTimestamp();
      log.send({ embeds: [embed] });
    }

    return message.channel.send(`✅ Removed ${amount} RP from <@${user.id}>. New RP: ${p.rp}`);
  }

  /* ===== PROFILE ===== */
  if (cmd === 'profile' || cmd === 'pf') {
    const user = message.mentions.users.first() || message.author;
    initPlayer(user.id);

    const p = players.get(user.id);
    const rank = getRank(p.rp);
    const badge = rankBadges.get(rank) || '⬜';
    const total = p.wins + p.losses;
    const wr = total ? ((p.wins / total) * 100).toFixed(1) : '0.0';

    const embed = new EmbedBuilder()
      .setColor(0x00ffff)
      .setAuthor({ name: 'Pokémon Ranked Profile', iconURL: user.displayAvatarURL() })
      .setThumbnail(user.displayAvatarURL())
      .addFields(
        { name: '🏅 Rank', value: `${badge} ${rank}`, inline: true },
        { name: '⭐ RP', value: `${p.rp}`, inline: true },
        { name: '🏆 Wins', value: `${p.wins}`, inline: true },
        { name: '❌ Losses', value: `${p.losses}`, inline: true },
        { name: '📊 Win Rate', value: `${wr}%`, inline: true }
      )
      .setTimestamp();

    const row = new ActionRowBuilder().addComponents(
      new ButtonBuilder()
        .setCustomId(`profile_refresh_${user.id}`)
        .setLabel('Refresh')
        .setEmoji('🔄')
        .setStyle(ButtonStyle.Primary),
      new ButtonBuilder()
        .setCustomId(`profile_close_${user.id}`)
        .setLabel('Close')
        .setEmoji('🗑️')
        .setStyle(ButtonStyle.Secondary)
    );

    return message.channel.send({ embeds: [embed], components: [row] });
  }

  /* ===== LEADERBOARD ===== */
  if (cmd === 'lb') {
    const leaderboard = getLeaderboard();

    if (leaderboard.length === 0) {
      return message.reply('No players on the leaderboard yet!');
    }

    const totalPages = Math.ceil(leaderboard.length / 10);
    const page = 0;

    const embed = await createLeaderboardEmbed(leaderboard, page, totalPages);
    const row = createLeaderboardButtons(page, totalPages);

    return message.channel.send({ embeds: [embed], components: [row] });
  }

  /* ===== LOG ===== */
  if (cmd === 'log') {
    const target = message.mentions.users.first();
    if (!target) return message.reply('Mention an opponent.');
    if (target.id === message.author.id) return message.reply('You cannot log a match against yourself.');

    initPlayer(message.author.id);
    initPlayer(target.id);

    const p1 = players.get(message.author.id);
    const p2 = players.get(target.id);

    const r1 = getRank(p1.rp);
    const r2 = getRank(p2.rp);

    const embed = new EmbedBuilder()
      .setTitle('Ranked Match Confirmation')
      .setColor(0xffaa00)
      .setDescription(`${target}, do you accept defeat against ${message.author}?`)
      .addFields(
        { name: 'Your Rank', value: r2, inline: true },
        { name: 'Opponent Rank', value: r1, inline: true }
      );

    const row = new ActionRowBuilder().addComponents(
      new ButtonBuilder().setCustomId(`accept_${message.author.id}_${target.id}`).setLabel('Accept').setStyle(ButtonStyle.Success),
      new ButtonBuilder().setCustomId(`reject_${message.author.id}_${target.id}`).setLabel('Reject').setStyle(ButtonStyle.Danger)
    );

    message.channel.send({ embeds: [embed], components: [row] });
  }
});

/* ========== BUTTONS ========== */

client.on('interactionCreate', async interaction => {
  if (!interaction.isButton()) return;

  if (interaction.customId === 'help_close')
    return interaction.message.delete();

  const parts = interaction.customId.split('_');

  /* PROFILE BUTTONS */
  if (parts[0] === 'profile') {
    const action = parts[1];
    const userId = parts[2];

    if (interaction.user.id !== userId)
      return interaction.reply({ content: 'Not your profile.', ephemeral: true });

    if (action === 'close') return interaction.message.delete();

    if (action === 'refresh') {
      initPlayer(userId);
      const p = players.get(userId);
      const rank = getRank(p.rp);
      const badge = rankBadges.get(rank) || '⬜';
      const total = p.wins + p.losses;
      const wr = total ? ((p.wins / total) * 100).toFixed(1) : '0.0';
      const user = await client.users.fetch(userId);

      const embed = EmbedBuilder.from(interaction.message.embeds[0])
        .setThumbnail(user.displayAvatarURL())
        .setFields(
          { name: '🏅 Rank', value: `${badge} ${rank}`, inline: true },
          { name: '⭐ RP', value: `${p.rp}`, inline: true },
          { name: '🏆 Wins', value: `${p.wins}`, inline: true },
          { name: '❌ Losses', value: `${p.losses}`, inline: true },
          { name: '📊 Win Rate', value: `${wr}%`, inline: true }
        )
        .setTimestamp();

      return interaction.update({ embeds: [embed] });
    }
  }

  /* LEADERBOARD BUTTONS */
  if (parts[0] === 'lb') {
    const action = parts[1];
    const currentPage = parseInt(parts[2]);

    const leaderboard = getLeaderboard();
    const totalPages = Math.ceil(leaderboard.length / 10);

    let newPage = currentPage;
    if (action === 'prev' && currentPage > 0) newPage--;
    if (action === 'next' && currentPage < totalPages - 1) newPage++;

    const embed = await createLeaderboardEmbed(leaderboard, newPage, totalPages);
    const row = createLeaderboardButtons(newPage, totalPages);

    return interaction.update({ embeds: [embed], components: [row] });
  }

  /* MATCH BUTTONS */
  const [action, winnerId, loserId] = parts;
  const isAdmin = interaction.member.roles.cache.has(ADMIN_ROLE_ID);

  if (action !== 'force' && interaction.user.id !== loserId)
    return interaction.reply({ content: 'Not for you.', ephemeral: true });

  if (action === 'force' && !isAdmin)
    return interaction.reply({ content: 'Admins only.', ephemeral: true });

  if (action === 'reject')
    return interaction.update({ content: '❌ Match rejected.', components: [] });

  initPlayer(winnerId);
  initPlayer(loserId);

  const wp = players.get(winnerId);
  const lp = players.get(loserId);

  const change = rpChange(getRank(wp.rp), getRank(lp.rp));
  if (!change) return;

  // Check for top 5 bonus
  const top5 = getLeaderboard(5).map(p => p.id);
  const bonus = top5.includes(loserId) ? 0.8 : 0;

  wp.rp += change.win + bonus;
  lp.rp = Math.max(0, lp.rp + change.loss);
  wp.wins++;
  lp.losses++;
  savePlayers();

  const log = interaction.guild.channels.cache.get(LOG_CHANNEL_ID);
if (log) {
  const embed = new EmbedBuilder()
    .setTitle('Pokétwo Duel Log')
    .setColor(0x00ffcc)
    .addFields(
      { name: 'Winner', value: `<@${winnerId}>`, inline: true },
      { name: 'Loser', value: `<@${loserId}>`, inline: true },
      { name: 'RP Gained', value: `${change.win}${bonus ? ` + ${bonus} (Top 5 Bonus)` : ''}`, inline: true }
    )
    .setTimestamp();
  log.send({ embeds: [embed] });
}

interaction.update({
  content: `✅ Ranked match logged!\n🏆 <@${winnerId}> defeated <@${loserId}>${bonus ? `\n🎉 Bonus +${bonus} RP for defeating a top 5 player!` : ''}`,
  components: []
});
});

/* ========== READY ========== */

client.once('ready', () => {
  loadPlayers();
  loadBadges();
  console.log(`✅ Logged in as ${client.user.tag}`);
});

client.login(TOKEN);
