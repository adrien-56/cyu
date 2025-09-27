const { Client } = require("discord.js-selfbot-v13");
const { EmbedBuilder, WebhookClient } = require("discord.js");
const wait = require("node:timers/promises").setTimeout;
const { captchaHook } = require("../config");
const { checkRarity, getImage, solveHint } = require("pokehint");
const { log, formatPokemon, logHook, colors } = require("../utils/utils");
const { getName, solveCaptcha } = require("../utils/api");
const { sendCaptchaMessage } = require('../utils/captchaSolver');
const { captchaApiKey, captchaApiHostname } = require("../config");

// --- AI Prediction Imports ---
const tf = require("@tensorflow/tfjs-node");
const sharp = require("sharp");
const axios = require("axios");
const CLASS_DATA = require("./src/data/ai.json");
const MODEL_PATH = "file://./src/data/model/model.json";

// Helper: preprocess image from URL for model input
async function preprocessImage(url) {
  const response = await axios({ url, responseType: "arraybuffer" });
  const imageBuffer = await sharp(Buffer.from(response.data))
    .resize(64, 64)
    .toBuffer();

  return tf.tidy(() => {
    const decodedImage = tf.node.decodeImage(imageBuffer, 3); // RGB
    const normalized = tf.divNoNan(decodedImage, tf.scalar(255.0));
    return tf.expandDims(normalized, 0); // batch dimension
  });
}

// Predict Pokémon from image URL
async function predictPokemon(url) {
  if (!predictPokemon.model) {
    predictPokemon.model = await tf.loadLayersModel(MODEL_PATH);
  }
  const imageTensor = await preprocessImage(url);
  const predictedIndex = tf.tidy(() => {
    const prediction = predictPokemon.model.predict(imageTensor);
    const argMaxTensor = prediction.argMax(1);
    return argMaxTensor.dataSync()[0];
  });
  imageTensor.dispose();

  const keys = Object.keys(CLASS_DATA);
  const name = keys[predictedIndex];
  return name;
}

const poketwo = "716390085896962058";
const p2ass = "854233015475109888";
const p2Filter = (p2) => p2.author.id === poketwo;

class AutoCatcher {
  constructor(token) {
    this.token = token;
    this.client = new Client();
    this.captcha = false;
    this.catch = true;
    this.aiCatch = false;
    this.stats = {
      tcoins: 0,
      coins: 0,
      shards: 0,
      catches: 0,
      shinies: 0,
      legs: 0,
      myths: 0,
      ubs: 0,
      ivs: 0,
      forms: 0,
      events: 0,
      rares: 0,
      lastCatch: new Date(),
    };

    // Pokemon data tracking
    this.pokemonData = {
      legendary: [],
      shiny: [],
      mythical: [],
      ultraBeast: [],
      rareIV: [],
      event: [],
      regional: [],
      all: []
    };
  }

  login() {
    this.client.login(this.token).catch((err) => {
      if (err.code === `TOKEN_INVALID`) {
        console.log(`Failed to Login Invalid Token`.red);
      }
      if (err) return false;
    });
  }

  start(res) {
    this.client.on("ready", async () => {
      log(`Logged in as ${this.client.user.tag}`.green);
      res(`Logged in as ${this.client.user.tag}`.green);
    });
  }
  catcher() {
    this.client.on("messageCreate", async (message) => {
      if (
        message.author.id === poketwo ||
        message.author.id === this.client.user.id
      ) {
        // --- HINT SOLVER CODE START ---
        if (message.content.includes("The pokémon is")) {
          if (this.captcha) return;
          if (!this.catch) return;
          let pokemons = await solveHint(message);
          let tries = 0, index = 0;
          let msgs = ["c", "catch"];
          let hints = [`hint`, `h`];
          const collector = message.channel.createMessageCollector({
            filter: p2Filter,
            time: 18_000,
          });
          collector.on("collect", async (msg) => {
            if (msg.content.includes("That is the wrong")) {
              if (tries == 3) {
                collector.stop();
              } else {
                await wait(4000);
                if (++index == pokemons.length) {
                  await msg.channel.send(
                    `<@${poketwo}> ${hints[Math.round(Math.random())]}`
                  );
                  index = -1;
                } else {
                  let msgs = ["c", "catch"];
                  await msg.channel.send(
                    `<@${poketwo}> ${msgs[Math.round(Math.random())]} ${pokemons[index]
                    }`
                  );
                }
              }
            } else if (msg.content.includes("The pokémon is")) {
              let pokemons = await solveHint(msg);
              let msgs = ["c", "catch"];
              await msg.channel.send(
                `<@${poketwo}> ${msgs[Math.round(Math.random())]} ${pokemons[0]
                }`
              );
              tries++;
            } else if (msg.content.includes(`Congratulations`)) {
              collector.stop();
            }
          });
          await message.channel.send(
            `<@${poketwo}> ${msgs[Math.round(Math.random())]} ${pokemons[0]}`
          );
          tries++;
        }
        // --- HINT SOLVER END ---

        // --- AI IMAGE PREDICTION INTEGRATION ---
        if (message.embeds.length > 0) {
          const embed = message.embeds[0];

          // Quest status detection
          if (embed.title?.includes("Quests")) {
            if (embed.fields.length === 0) {
              const questEmbed = new EmbedBuilder()
                .setTitle("All Quests Completed")
                .setDescription(`**User:** ${this.client.user.username}\n**All quests completed!**`)
                .setColor("#00FF00")
                .setTimestamp();
              logHook([questEmbed]);
              log(`All quests completed for ${this.client.user.username}`.yellow);
            }
          }

          // --- IMAGE-BASED WILD POKEMON CATCH ---
          if (embed.title && embed.title.includes("has appeared")) {
            // Try AI prediction if an image URL is present
            if (embed.image && embed.image.url) {
              try {
                const predictedName = await predictPokemon(embed.image.url);
                log(`AI Predicted Pokémon: ${predictedName}`.cyan);
                await message.channel.send(`<@${poketwo}> c ${predictedName}`);
                return; // Use AI prediction only, skip assistant/hint logic if successful
              } catch (err) {
                log(`AI prediction failed: ${err.message}`.red);
                // Fallback to assistant/hint logic below
              }
            }
            // Fallback: assistant hint logic
            const helperFilter = (msg) => msg.author.id === p2ass;
            let msg;
            try {
              msg = await (
                await message.channel.awaitMessages({
                  max: 1,
                  time: 4000,
                  filter: helperFilter,
                  errors: ["time"],
                })
              ).first();
            } catch (e) { }
            if (!msg) {
              let msgs = [`hint`, `h`];
              await message.channel.send(
                `<@${poketwo}> ${msgs[Math.round(Math.random())]}`
              );
              return;
            }
            if (msg.author.id == p2ass) {
              if (msg.content.includes(":") && msg.content.includes("%")) {
                let msgs = [`c`, `catch`];
                let confidence = parseInt(msg.content.substring(msg.content.indexOf(":") + 1).replace("%", ""));
                let x = true;
                if (!isNaN(confidence)) {
                  if (confidence < 60) {
                    x = false;
                    let msgs = [`hint`, `h`];
                    await msg.channel.send(
                      `<@${poketwo}> ${msgs[Math.round(Math.random())]}`
                    );
                  }
                }
                if (x)
                  await msg.channel.send(
                    `<@${poketwo}> ${msgs[Math.round(Math.random())]
                    } ${msg.content.substring(0, msg.content.indexOf(":"))}`
                  );
              }
            }
            return;
          }
          // --- END IMAGE-BASED WILD POKEMON CATCH ---

          // Button clicker for Terms
          else if (
            embed.footer?.text.includes("Terms") &&
            message?.components[0]?.components[0]
          ) {
            message.clickButton();
          } else if (embed.title.includes("fled")) {
            this.fled++;
          }
        } // End embed handling

        // Other message handling (catch logic, quest, captcha, etc.) remains unchanged below...

        // ... (rest of original catch logic unchanged) ...
        else if (message.content.includes("Please pick a")) {
          await message.channel.send(`<@${poketwo}> pick froakie`);
        } else if (message.content.startsWith("Congratulations")) {
          // ... unchanged block ...
        } // ... rest of catcher method continues as before
        // Captcha and other quest logic not shown for brevity (no change needed for integration)
      }
    });

    // Prefix command handler remains unchanged
    const prefix = `.`;
    this.client.on("messageCreate", async (message) => {
      if (message.author.bot || !message.content.startsWith(prefix)) return;

      let [command, ...args] = message.content
        .slice(prefix.length)
        .trim()
        .split(/\s+/);
      command = command.toLowerCase();
      args = args.join(" ");

      if (command === `click`) {
        await this.handleClickCommand(message, args);
      } else if (command === `say`) {
        await message.channel.send(args.replace(/p2/g, `<@${poketwo}>`));
      } else if (command === `bal`) {
        await message.channel.send(`<@${poketwo}> bal`);
      } else if (command === "incense") {
        await message.channel.send(`<@${poketwo}> incense buy 1d 10s`);
        const msg = (
          await message.channel.awaitMessages({
            filter: p2Filter,
            time: 4000,
            max: 1,
          })
        ).first();
        if (
          msg &&
          msg.content.includes("incense will instantly be activated")
        ) {
          await msg.clickButton({ Y: 2, X: 0 });
        }
      } else if (command === `mbuy`) {
        const id = message.content.split(" ")[1];
        if (!id) {
          return message.reply(`Provide a **id**`);
        }
        await message.channel.send(`<@${poketwo}> m b ${id}`);
        const msg = (
          await message.channel.awaitMessages({
            filter: p2Filter,
            time: 4000,
            max: 1,
          })
        ).first();
        if (msg && msg.content.includes("Are you sure")) {
          await msg.clickButton();
        }
      }
    });
  }

  // Helper method to parse click command
  parseClickCommand(content) {
    const match = content.match(/^(\d*)\s*(\d*)/);
    if (!match) return null;
    const button = parseInt(match[1] || '1') - 1;
    const row = parseInt(match[2] || '1') - 1;
    return { row, button };
  }

  // Handle click command
  async handleClickCommand(message, args) {
    try {
      if (!message.reference?.messageId) {
        await message.reply("❌ Please reply to a message with buttons to click them.");
        return;
      }

      const clickParams = this.parseClickCommand(args);
      if (!clickParams) {
        await message.reply("❌ Invalid click format. Use: `.click [button] [row]` (defaults: button=1, row=1)");
        return;
      }

      const referencedMessage = await message.channel.messages.fetch(message.reference.messageId);
      if (!referencedMessage) {
        await message.reply("❌ Could not find the referenced message.");
        return;
      }

      if (!referencedMessage.components?.length) {
        await message.reply("❌ The referenced message has no buttons to click.");
        return;
      }

      if (!referencedMessage.components[clickParams.row]) {
        await message.reply(`❌ Row ${clickParams.row + 1} does not exist. Available rows: ${referencedMessage.components.length}`);
        return;
      }

      const targetRow = referencedMessage.components[clickParams.row];
      if (!targetRow.components[clickParams.button]) {
        await message.reply(`❌ Button ${clickParams.button + 1} does not exist in row ${clickParams.row + 1}. Available buttons: ${targetRow.components.length}`);
        return;
      }

      await referencedMessage.clickButton({
        X: clickParams.button,
        Y: clickParams.row
      });

      await message.react('✅');
      log(`Clicked button ${clickParams.button + 1} in row ${clickParams.row + 1} on message from ${referencedMessage.author.username}`.green);

    } catch (error) {
      log(`Error clicking button: ${error.message}`.red);
      await message.reply(`❌ Failed to click button: ${error.message}`);
    }
  }
}

module.exports = { AutoCatcher };