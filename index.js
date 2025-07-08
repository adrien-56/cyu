const axios = require("axios");
const fs = require("fs");
const os = require("os");
const readline = require("readline");
const imaps = require("imap-simple");
const cheerio = require("cheerio");
const { DateTime } = require("luxon");
const puppeteer = require("puppeteer"); // Use Playwright by changing the import and browser logic

// === ADVANCED CONFIGURATION ===
const MAILTM_API = "https://api.mail.tm";
const IMAP_SERVER = "imap.mail.tm";
const IMAP_PORT = 993;
const MAIL_SUBJECT_KEYWORD = "verify";
const WAIT_TIMEOUT = 180000; // ms
const POLL_INTERVAL = 5000; // ms
const DISCORD_PASSWORD_LENGTH = 16;
const DISCORD_PASSWORD_CHARS =
  "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*-_";
const DISCORD_REGISTRATION_URL = "https://discord.com/register";
const USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";
const BIRTH_YEAR_RANGE = [1990, 2005];
const BIRTH_MONTHS = [
  "JANUARY",
  "FEBRUARY",
  "MARCH",
  "APRIL",
  "MAY",
  "JUNE",
  "JULY",
  "AUGUST",
  "SEPTEMBER",
  "OCTOBER",
  "NOVEMBER",
  "DECEMBER",
];

// --- TOGGLE/SETTINGS ---
const USE_PROXY = true;
const HEADLESS = false;
const PROXY_LIST_FILE = "proxies.txt";
const DISCORD_BOT_WEBHOOK =
  "https://discord.com/api/webhooks/WEBHOOKID/TOKEN"; // Replace with your webhook url

const banner = `
██████╗ ██╗██╗   ██╗███████╗██████╗ 
██╔══██╗██║██║   ██║██╔════╝██╔══██╗
██████╔╝██║██║   ██║█████╗  ██████╔╝
██╔══██╗██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
██║  ██║██║ ╚████╔╝ ███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝
            Ricer
      by .kevhhh
`;

function timestamp() {
  return `[${DateTime.now().toFormat("HH:mm:ss dd-MM-yyyy")}]`;
}

function randomPassword(length = DISCORD_PASSWORD_LENGTH) {
  const chars = DISCORD_PASSWORD_CHARS;
  let out = "";
  for (let i = 0; i < length; i++)
    out += chars.charAt(Math.floor(Math.random() * chars.length));
  return out;
}

function randomUsername(length = 10) {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let out = "";
  for (let i = 0; i < length; i++)
    out += chars.charAt(Math.floor(Math.random() * chars.length));
  return out;
}

function randomDisplayname() {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
  const length = Math.floor(Math.random() * 7) + 6;
  let out = "";
  for (let i = 0; i < length; i++)
    out += chars.charAt(Math.floor(Math.random() * chars.length));
  return out;
}

function randomBirthdate() {
  const day = String(Math.floor(Math.random() * 28) + 1);
  const month = BIRTH_MONTHS[Math.floor(Math.random() * BIRTH_MONTHS.length)];
  const year =
    Math.floor(
      Math.random() * (BIRTH_YEAR_RANGE[1] - BIRTH_YEAR_RANGE[0] + 1)
    ) + BIRTH_YEAR_RANGE[0];
  return [day, month, year.toString()];
}

function loadProxies() {
  if (!fs.existsSync(PROXY_LIST_FILE)) {
    console.log(
      `${timestamp()} No proxies.txt found, running without proxy.`
    );
    return [];
  }
  const proxies = fs
    .readFileSync(PROXY_LIST_FILE, "utf-8")
    .split(/\r?\n/)
    .filter((l) => l.trim());
  if (!proxies.length) {
    console.log(
      `${timestamp()} No proxies loaded, running without proxy.`
    );
  }
  return proxies;
}

function getRandomProxy() {
  const proxies = loadProxies();
  if (!proxies.length) return null;
  const proxy = proxies[Math.floor(Math.random() * proxies.length)];
  if (proxy.includes("@")) {
    const [auth, addr] = proxy.split("@");
    const [host, port] = addr.split(":");
    const [user, pwd] = auth.split(":");
    return {
      http: `http://${user}:${pwd}@${host}:${port}`,
      https: `http://${user}:${pwd}@${host}:${port}`,
      browser: `http://${user}:${pwd}@${host}:${port}`,
    };
  } else if (proxy.includes(":")) {
    const [host, port] = proxy.split(":");
    return {
      http: `http://${host}:${port}`,
      https: `http://${host}:${port}`,
      browser: `http://${host}:${port}`,
    };
  }
  return null;
}

async function mailtmCreateAccount(proxies = null) {
  const instance = axios.create();
  // Proxy for axios is not implemented here
  const domResp = await instance.get(`${MAILTM_API}/domains`, { timeout: 30000 });
  const domain = domResp.data["hydra:member"][0]["domain"];
  const username = randomUsername();
  const email_addr = `${username}@${domain}`;
  const password = randomPassword(14);

  const accResp = await instance.post(
    `${MAILTM_API}/accounts`,
    {
      address: email_addr,
      password: password,
    },
    { timeout: 30000 }
  );
  console.log(
    `${timestamp()} Mail.tm account created: ${email_addr}`
  );
  return [email_addr, password];
}

async function waitForVerificationEmailImap(
  email_addr,
  password,
  subject_contains = "verify",
  timeout = WAIT_TIMEOUT,
  poll_interval = POLL_INTERVAL
) {
  const config = {
    imap: {
      user: email_addr,
      password: password,
      host: IMAP_SERVER,
      port: IMAP_PORT,
      tls: true,
      authTimeout: 10000,
    },
  };
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      const connection = await imaps.connect(config);
      await connection.openBox("INBOX");
      const searchCriteria = ["ALL"];
      const fetchOptions = { bodies: ["HEADER", "TEXT"], struct: true };
      const messages = await connection.search(searchCriteria, fetchOptions);
      for (let i = messages.length - 1; i >= 0; i--) {
        const header = messages[i].parts.find((x) => x.which === "HEADER");
        const subject = header.body.subject ? header.body.subject[0] : "";
        if (subject && subject.toLowerCase().includes(subject_contains.toLowerCase())) {
          let body = "";
          const textPart = messages[i].parts.find((x) => x.which === "TEXT");
          body = textPart.body;
          connection.end();
          return { subject, body };
        }
      }
      connection.end();
    } catch (e) {
      console.log(`${timestamp()} IMAP error: ${e}`);
    }
    await new Promise((r) => setTimeout(r, poll_interval));
  }
  throw new Error("No verification email received in time.");
}

function extractVerificationLinkFromHtml(html) {
  const links = [];
  const $ = cheerio.load(html);
  $("a").each((i, e) => {
    const href = $(e).attr("href");
    if (href && href.startsWith("https://")) links.push(href);
  });
  // fallback to regex if needed
  if (!links.length) {
    const regex = /https:\/\/[^\s"'<>]+/g;
    let match;
    while ((match = regex.exec(html))) {
      links.push(match[0]);
    }
  }
  for (const link of links) {
    if (link.includes("discord.com/verify") || link.includes("discord.com/email"))
      return link;
  }
  return links[0] || null;
}

async function sendTokenToWebhook(email, password, token) {
  const data = {
    embeds: [
      {
        title: "New Verified Discord Token",
        color: 0x00ff00,
        fields: [
          { name: "Token", value: `||${token}||`, inline: false },
          { name: "Email", value: email, inline: true },
          { name: "Password", value: password, inline: true },
          {
            name: "Time",
            value: DateTime.now().toFormat("yyyy-MM-dd HH:mm:ss"),
            inline: false,
          },
        ],
        footer: { text: "Ricer by .kevhhh" },
      },
    ],
  };
  try {
    const resp = await axios.post(DISCORD_BOT_WEBHOOK, data);
    if ([200, 204].includes(resp.status)) {
      console.log(`${timestamp()} Token sent to Discord webhook!`);
    } else {
      console.log(
        `${timestamp()} Failed to send token to webhook: ${resp.status} ${resp.statusText}`
      );
    }
  } catch (e) {
    console.log(
      `${timestamp()} Failed to send token to webhook: ${e.response?.status} ${e.response?.data}`
    );
  }
}

async function loginAndFetchToken(email, password, proxies = null) {
  const data = { email, password, undelete: "false" };
  const headers = {
    "content-type": "application/json",
    "user-agent": USER_AGENT,
  };
  const instance = axios.create();
  // Set up proxy here if needed
  try {
    const r = await instance.post(
      "https://discord.com/api/v9/auth/login",
      data,
      { headers, timeout: 30000 }
    );
    if (r.status === 200 && r.data.token) {
      const token = r.data.token;
      console.log(`${timestamp()} Token: ${token}`);
      await sendTokenToWebhook(email, password, token);
      return true;
    } else if (r.data && r.data.captcha_key) {
      console.log(
        `${timestamp()} Discord returned captcha, stopping retry.`
      );
      return false;
    } else {
      console.log(
        `${timestamp()} Failed to fetch token: ${r.status} ${JSON.stringify(r.data)}`
      );
    }
  } catch (e) {
    if (e.response) {
      console.log(
        `${timestamp()} Failed to fetch token: ${e.response.status} ${JSON.stringify(
          e.response.data
        )}`
      );
    } else {
      console.log(`${timestamp()} Error: ${e}`);
    }
  }
  return false;
}

function prettyStep(msg) {
  console.log(`${timestamp()} [STEP] ${msg}`);
}

async function askEnter(msg) {
  prettyStep(msg);
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise((resolve) => {
    rl.question("Press Enter to continue...", () => {
      rl.close();
      resolve();
    });
  });
}

async function fillDiscordRegistration(page, email_addr, global_name, username, discord_password, birth_day, birth_month, birth_year) {
  await page.goto(DISCORD_REGISTRATION_URL, { waitUntil: "networkidle2" });
  await page.waitForSelector('input[name="email"]', { timeout: 60000 });
  await page.type('input[name="email"]', email_addr);
  await page.type('input[name="global_name"]', global_name);
  await page.type('input[name="username"]', username);
  await page.type('input[name="password"]', discord_password);

  // Discord's react-select dropdowns (selectors may change!)
  await page.click('[aria-label="Day:"]');
  await page.keyboard.type(birth_day);
  await page.keyboard.press('Enter');

  await page.click('[aria-label="Month:"]');
  await page.keyboard.type(birth_month);
  await page.keyboard.press('Enter');

  await page.click('[aria-label="Year:"]');
  await page.keyboard.type(birth_year);
  await page.keyboard.press('Enter');

  await page.waitForSelector('button[type="submit"]');
  await page.click('button[type="submit"]');
}

async function main() {
  console.clear();
  console.log(banner);
  while (true) {
    let proxies = USE_PROXY ? getRandomProxy() : null;
    let username = randomUsername();
    let global_name = randomDisplayname();
    let [birth_day, birth_month, birth_year] = randomBirthdate();
    let discord_password = randomPassword();
    let [email_addr, email_pass] = await mailtmCreateAccount(proxies);

    prettyStep(
      `Using temp email: ${email_addr}, Username: ${username}, Display: ${global_name}, Password: ${discord_password}, Proxy: ${proxies ? proxies.browser : "None"}`
    );

    // Puppeteer launch
    let puppeteerArgs = [
      `--user-agent=${USER_AGENT}`
    ];
    if (proxies && proxies.browser) {
      puppeteerArgs.push(`--proxy-server=${proxies.browser}`);
    }
    const browser = await puppeteer.launch({ headless: HEADLESS, args: puppeteerArgs });
    const page = await browser.newPage();

    try {
      await fillDiscordRegistration(page, email_addr, global_name, username, discord_password, birth_day, birth_month, birth_year);

      await askEnter(
        "Solve the CAPTCHA in the browser, then press Enter here when registration is complete."
      );
      prettyStep("Waiting for verification email via IMAP...");

      try {
        const mail = await waitForVerificationEmailImap(
          email_addr,
          email_pass,
          MAIL_SUBJECT_KEYWORD,
          WAIT_TIMEOUT,
          POLL_INTERVAL
        );
        console.log(
          `${timestamp()} Verification email received: ${mail.subject}`
        );
        const link = extractVerificationLinkFromHtml(mail.body);
        if (link) {
          prettyStep("Opening verification link in browser...");
          await page.goto(link, { waitUntil: "networkidle2" });
          await askEnter(
            "If there is a CAPTCHA on the verification page, solve it. Press Enter once the account is verified in the browser..."
          );
          await new Promise((r) => setTimeout(r, 5000));
        } else {
          console.log(
            `${timestamp()} Could not extract verification link from email.`
          );
        }
      } catch (e) {
        console.log(
          `${timestamp()} Verification email did not arrive in time.`
        );
      }

      prettyStep("Trying to fetch Discord token...");
      const success = await loginAndFetchToken(
        email_addr,
        discord_password,
        proxies
      );
      if (success) {
        console.log(
          `${timestamp()} Account created and verified! Restarting...`
        );
      } else {
        console.log(`${timestamp()} Failed to fetch the token.`);
      }
    } catch (e) {
      console.log(`${timestamp()} Error: ${e}`);
    } finally {
      await browser.close();
    }
  }
}

if (require.main === module) {
  main();
}
