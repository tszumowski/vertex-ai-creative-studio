import mesop as me

NUMBER_OF_IMAGES_OPTIONS = [
    me.SelectOption(label="1", value="1"),
    me.SelectOption(label="2", value="2"),
    me.SelectOption(label="3", value="3"),
    me.SelectOption(label="4", value="4"),
]

MASK_MODE_OPTIONS = [
    me.SelectOption(
        label="Foreground",
        value="foreground",
    ),
    me.SelectOption(
        label="Background",
        value="background",
    ),
    me.SelectOption(
        label="Semantic",
        value="semantic",
    ),
]

EDIT_MODE_OPTIONS = [
    me.SelectOption(
        label="Outpainting",
        value="EDIT_MODE_OUTPAINT",
    ),
    me.SelectOption(
        label="Inpainting insert",
        value="EDIT_MODE_INPAINT_INSERTION",
    ),
    me.SelectOption(
        label="Inpainting removal",
        value="EDIT_MODE_INPAINT_REMOVAL",
    ),
    # Not available, yet.
    # me.SelectOption(
    #    label="Product image",
    #    value="EDIT_MODE_PRODUCT_IMAGE",
    # ),
    #
    me.SelectOption(
        label="Background swap",
        value="EDIT_MODE_BGSWAP",
    ),
]

COMPOSITION_OPTIONS = [
    me.SelectOption(label="None", value="None"),
    me.SelectOption(label="Closeup", value="Closeup"),
    me.SelectOption(label="Knolling", value="Knolling"),
    me.SelectOption(label="Landscape photography", value="Landscape photography"),
    me.SelectOption(
        label="Photographed through window", value="Photographed through window"
    ),
    me.SelectOption(label="Shallow depth of field", value="Shallow depth of field"),
    me.SelectOption(label="Shot from above", value="Shot from above"),
    me.SelectOption(label="Shot from below", value="Shot from below"),
    me.SelectOption(label="Surface detail", value="Surface detail"),
    me.SelectOption(label="Wide angle", value="Wide angle"),
]

LIGHTING_OPTIONS = [
    me.SelectOption(label="None", value="None"),
    me.SelectOption(label="Backlighting", value="Backlighting"),
    me.SelectOption(label="Dramatic light", value="Dramatic light"),
    me.SelectOption(label="Golden hour", value="Golden hour"),
    me.SelectOption(label="Long-time exposure", value="Long-time exposure"),
    me.SelectOption(label="Low lighting", value="Low lighting"),
    me.SelectOption(label="Multiexposure", value="Multiexposure"),
    me.SelectOption(label="Studio light", value="Studio light"),
    me.SelectOption(label="Surreal lighting", value="Surreal lighting"),
]

COLOR_AND_TONE_OPTIONS = [
    me.SelectOption(label="None", value="None"),
    me.SelectOption(label="Black and white", value="Black and white"),
    me.SelectOption(label="Cool tone", value="Cool tone"),
    me.SelectOption(label="Golden", value="Golden"),
    me.SelectOption(label="Monochromatic", value="Monochromatic"),
    me.SelectOption(label="Muted color", value="Muted color"),
    me.SelectOption(label="Pastel color", value="Pastel color"),
    me.SelectOption(label="Toned image", value="Toned image"),
]

CONTENT_TYPE_OPTIONS = [
    me.SelectOption(label="None", value="None"),
    me.SelectOption(label="Photo", value="Photo"),
    me.SelectOption(label="Art", value="Art"),
]

ASPECT_RATIO_OPTIONS = [
    me.SelectOption(label="1:1", value="1:1"),
    me.SelectOption(label="3:4", value="3:4"),
    me.SelectOption(label="4:3", value="4:3"),
    me.SelectOption(label="16:9", value="16:9"),
    me.SelectOption(label="9:16", value="9:16"),
]

IMAGE_MODEL_OPTIONS = [
    me.SelectOption(label="Imagen 3 Fast", value="imagen-3.0-fast-generate-001"),
    me.SelectOption(label="Imagen 3", value="imagen-3.0-generate-001"),
]

RANDOM_PROMPTS = [
    "A studio photo of five scientists standing around an engineering device and discussing their latest discovery, natural bright lighting, eye level lens, people dressed in business casuals clothes, Canon",
    "a photo of a young woman and her dog at the park, the woman wears a green blouse, the dog is a small yorkie and has a green collar, the woman smiles and faces the camera, a lake can be seen in the background, natural lightning",
    "A close up image of four pairs of hands on a table",
    "A polaroid capture of three friends happy on the car bonnet, late 1960s america, flash photography",
    "a polaroid capture of high school friends happy on the car bonnet, late 1960s america, flash photography",
    "a recreation of the oil painting The Meeting Fox Hunt Scene where spider-man is riding the horse",
    "Contrast with huge height difference, a person looks upon a massive cloud, extremely detailed still from, hyper textured, anime style",
    "in a white bowl in a sunlit kitchen, a close-up photo showcases a heaping pile of golden-brown Homemade French Fries, crisply cooked in an Air Fryer. The high-resolution image captures the inviting texture and glistening oils, highlighting the perfect combination of fluffy insides and crunchy exteriors. Steam gently rises from the fries, filling the frame with a sense of warmth and anticipation.",
    "An old woman but super modern and cool, her is smiling and wearing yellow modern and nice clothes, using her high-tech cellphone to take selfie in her beautiful garden, happy atmosphere, high resolution",
    "A polaroid capture of three friends happy on the car bonnet, late 1960s america, flash photography",
    "a photorealistic image of a woman’s hand reaching up to touch a dandelion seed head, a field of dandelions stretching to the horizon, with the phrase 'Sometimes letting go is the bravest act' written in delicate cursive above the hand",
    "artist painting",
    'A Real-Cola bottle showing the Real-Cola logo with a blue sticker with the text: "Happy Halloween"',
    "From a rooftop garden, a group of urban farmers, their hands caked in soil, proudly harvest their bountiful crops, the cityscape stretching out behind them like a vibrant tapestry on a sunny day",
    'a card for a university graduate, says "Congratulations new grad!" on the cover, with a cute cartoon of a young adult wearing graduation robes, in a fun playful color and design',
    'a card for a university graduate, says "new grad" on the cover, with a cute cartoon of a young adult wearing graduation robes, in a fun playful color and design',
    "A hiker during a late spring day in California’s Big Sur overlooking the ocean",
    "a family of four sitting at the couch watching tv with their dog",
    "A photo of 3 friends hiking in hawaii near a beach  in the mid afternoon",
    'design for a card for new weds, says "Congratulations Mila and Miko" on the cover, with a cute cartoon a couple, in fun playful color and design. Mila has brown hair with green eyes wearing a pink dress and carrying a bouquet of lily\'s. Miko has blue eyes, tan skin and short hair - he is wearing a blue suit',
    "In a sun-drenched open-air kitchen, a group of friends, their laughter echoing through the space, prepare a vibrant feast together, their hands stained with the colors of fresh herbs and spices.",
    "four friends (two men and two women) at the pyramids of Giza, the men are wearing polo shirts with khakhi shorts while the women are wearing floral dresses. They are all wearing sunglasses, and straw hats. Harsh direct sunlight, in the style of a travel photo",
    "four friends (two men and two women) at the steps under the pyramid of Giza, the men are wearing polo shirts with khakhi shorts while the women are wearing floral dresses. They are all wearing sunglasses, and straw hats. Harsh direct sunlight, in the style of a travel photo",
    "close up shot, In a dimly lit jazz club, a soulful saxophone player, their face contorted in concentration, pours their heart out through their music. A small group of people listen intently, feeling every emotion",
    "In a bustling newsroom, a team of journalists, their eyes glued to computer screens, race against the clock to break a major story, their fingers flying across keyboards as they craft compelling narratives.",
    "a rembrandt painting of a clean shaven 36 year old male with short light strawberry brown hair",
    "Isometric drawing of the ocean featuring marine animals like fish, dolphins. Displaying different levels of seabed. Penguins and polar bears stand on the top iceberg, with a theme of ocean conservation, surrealism, and a dreamy blue background",
    "Graffiti art style poster, stylized cartoon style, a vintage car on a busy street, low angle, car reflection visible on a puddle in the street, dirty, grungy",
    "a modern and bright Tuscan villa, into which the sun shines and sparkles. natural green and grey colors. modern interior that inspires with freshness, light and playfulness, architecture photography, simple view, minimalism",
    "Mock up of a modern dining room interior design, creative, dreamy aesthetic",
    "architectural photography, a small grill on a minimalist concrete surface, modern design, sharp details, ambient light, shadows, ultra-realistic texture",
    "Stock photo of a person sailing on a calm sea with a beautiful sunset for advertisement, well-composed, well-lit, in focus, with good resolution and clarity",
    "ferrari Formula one car, side angle, photo realistic,  hyper real, black background, sharp lighting, dramatic photography",
    "a spacious personal office in a luxury home, floor to ceiling windows, dim natural light, covered in plants, a rainy forest view, embodies serenity, peace",
    "professional photograph of a high end scotch whiskey “Imagen” presented on the table, eye level, warm cinematic,",
    "A stock photograph of two friends having coffee with a bustling café as the background context, during the early afternoon with warm, ambient lighting and shot with a wide-angle lens",
    "iconic idol, flat vector, groovy neon lo lo-fi, isolated on a white background, surrounded by circle",
    "A serene lakeside scene at sunset with visible brushwork. Impasto texture and chiaroscuro lighting, emulating the style of a classical oil painting",
    "ऊपर से देखा गया किताबों का ढेर। सबसे ऊपरी पुस्तक में एक पक्षी का जलरंग चित्रण है। किताब पर VERTEX AI मोटे अक्षरों में लिखा हुआ है",
    "어두운 노란색과 청록색으로 이루어진 밝은 색의 옷을입고 귀걸이를 끼고있는 여자 포스트 모던 패션 사진",
    "A large, colorful bouquet of flowers in an old blue glass vase on the table. In front is one beautiful peony flower surrounded by various other blossoms like roses, lilies, daisies, orchids, fruits, berries, green leaves. The background is dark gray. Oil painting in the style of the Dutch Golden Age.",
    "Detailed illustration of majestic lion roaring proudly in a dream-like jungle, purple white line art background, clipart on light violet paper texture",
    "Claymation scene. A medium wide shot of an elderly woman. She is wearing flowing clothing. She is standing in a lush garden watering the plants with an orange watering can",
    "Elephant amigurumi walking in savanna, a professional photograph, blurry background",
    "A view of a person's hand as they hold a little clay figurine of a bird in their hand and sculpt it with a modeling tool in their other hand. You can see the sculptor's scarf. Their hands are covered in clay dust. a macro DSLR image highlighting the texture and craftsmanship.",
    "White fluffy bear toy is sleeping in a children's room, on the floor of a baby bedroom with toy boxes and toys around, in the style of photorealistic 3D rendering.",
    'Word "light" made from various colorful feathers, black background',
    "A single comic book panel of a boy and his father on a grassy hill, staring at the sunset. A speech bubble points from the boy's mouth and says: The sun will rise again. Muted, late 1990s coloring style",
    'A photograph of a stately library entrance with the words "Central Library" carved into the stone',
    "Shot in the style of DSLR camera with the polarizing filter. A photo of two hot air balloons floating over the unique rock formations in Cappadocia, Turkey. The colors and patterns on these balloons contrast beautifully against the earthy tones of the landscape below. This shot captures the sense of adventure that comes with enjoying such an experience.",
    "A close-up photo of an origami bird soaring through a cityscape, in a flock with others of different colors and patterns, casting intricate shadows on the buildings below.",
    "Three women stand together laughing, with one woman slightly out of focus in the foreground. The sun is setting behind the women, creating a lens flare and a warm glow that highlights their hair and creates a bokeh effect in the background. The photography style is candid and captures a genuine moment of connection and happiness between friends. The warm light of golden hour lends a nostalgic and intimate feel to the image.",
    "A weathered, wooden mech robot covered in flowering vines stands peacefully in a field of tall wildflowers, with a small bluebird resting on its outstretched hand. Digital cartoon, with warm colors and soft lines. A large cliff with a waterfall looms behind.",
    "Photographic portrait of a real life dragon resting peacefully in a zoo, curled up next to its pet sheep. Cinematic movie still, high quality DSLR photo.",
    "A view of a person’s hand holding a eucalyptus sprig - a macro DSLR image highlighting the balance of human and nature.",
    'Word "light" made from various colorful feathers, black background',
    "A single comic book panel of a boy and his father on a grassy hill, staring at the sunset. A speech bubble points from the boy's mouth and says: The sun will rise again. Muted, late 1990s coloring style",
    'A photograph of a stately library entrance with the words "Central Library" carved into the stone',
    "Photo of a felt puppet diorama scene of a tranquil nature scene of a secluded forest clearing with a large friendly, rounded robot is rendered in a risograph style. An owl sits on the robots shoulders and a fox at its feet. Soft washes of color, 5 color, and a light-filled palette create a sense of peace and serenity, inviting contemplation and the appreciation of natural beauty",
    "A photo of an Indian woman hugging her friend, both covered in Holi colors and smiling, celebrating the festival with joy. Realistic photography, taken in the style of DSLR camera with 35mm lens.",
    "Abstract cross-hatch sketch: a black and white sketch with loose hand in calligraphic ink showing the abstract outline in profile of a black panther poised on a branch. A canopy of trees is behind.",
    "A view of a knitter’s hands executing a complex weave on a striped hat - a macro DSLR image highlighting the warmth and connection with the earth and nature.",
    "A woman with blonde hair wearing sunglasses stands amidst a dazzling display of golden bokeh lights. Strands of lights and crystals partially obscure her face, and her sunglasses reflect the lights. The light is low and warm creating a festive atmosphere and the bright reflections in her glasses and the bokeh. This is a lifestyle portrait with elements of fashion photography.",
    "a portrait of an auto mechanic in her workshop, holding a wrench in one hand. a old sports car in the background, with a workbench and tools all around. bokeh, high quality dslr photograph.",
    "An origami owl made of brown paper is perched on a branch of an evergreen tree. The owl is facing forward with its eyes closed, giving it a peaceful appearance. The background is a blur of green foliage, creating a natural and serene setting.",
    "A weathered, wooden mech robot covered in flowering vines stands peacefully in a field of tall wildflowers, with a small bluebird resting on its outstretched metallic hand. Digital cartoon, with warm colors and soft lines. A large cliff with waterfall looms behind.",
    "Close-up, low angle view of a rabbit biting into a cabbage on a plate on a counter. A man wearing glasses is yelling at the rabbit and reaching out his hand to snatch the cabbage. High-contrast visuals and cinematic lighting. Fujifilm XF 10-24mm f/4, action shot.",
    "Photo of vinyl toy scene. A colossal stone robot adorned with giant stone gardening tools stands in a lush, futuristic garden. A single sprout peeks out from a patch of fertile soil nearby. Digital art with a soft, dreamlike quality. Vinyl miniature scene.",
    "A pair of well-worn hiking boots, caked in mud and resting on a rocky trail. There’s a squirrel’s head poking out of one of the boots. There’s a mountainous landscape in the background, captured with a Nikon D780.",
    "A joyful woman with a prosthetic leg and athletic attire celebrates reaching the summit of a snowy mountain. She stands triumphantly next to her snowboard, with the vast landscape stretching out behind her. captured with a Leica M11 rangefinder camera for a timeless, film-like aesthetic.",
    "Three women stand together outside with the sun setting behind them creating a lens flare. One woman in the foreground is slightly out of focus and wearing a black felt hat. The middle woman is in focus, wearing glasses, and laughing with her head tossed back. The third woman has blonde hair pulled back in a bun and is wearing a cream sweater. She is looking at the woman in glasses and smiling.",
    "Two contrasting figures, one wooden and jagged, the other smooth, diamond, embrace in a sun-drenched courtyard – the Harmony of Opposites.",
    'pixel art of a space shuttle blasting of, with "STS-1" written below it. Cape Canaveral in the background, blue skies, with plumes of smoke billowing out.',
    "A yellow toy submarine diving deep under the blue ocean. Close-up nature photography, sunlight coming through the water.",
    "A busy city street with people crossing the road at an intersection, illuminated by sunlight, showcasing diverse age groups and styles as they walk across zebra stripes on the pavement. The focus is sharp on one person in red , standing out against their surroundings. Shot during golden hour to capture the warm lighting effects.",
    "An antique pocket watch with Roman numerals and an ornate chain, lying on a worn leather surface with a vintage map in the background, captured with a Leica Q2.",
    "A cute 1970’s convertible sports car sits in front of a pub in an ink wash painting, capturing a charming English map in the background, captured with a Leica Q2.",
    "Joy shines in the eyes of a young woman, a charcoal portrait showing she’s ready to make a difference in the world.",
    "An elderly woman wearing a straw hat and a pink jacket is sitting next to a brown and white dog. Both the woman and the dog are looking off into the distance with serene expressions. The lighting is the warm, golden light of sunset, which creates a peaceful and contemplative atmosphere. This is a lifestyle portrait capturing a quiet moment.",
    "A long exposure photo of the Milky Way in a starry night sky, centered over an ocean beach at magic hour. The milky way is bright and prominent with many stars visible against a dark and a cinematic composition in the style. blue black atmosphere in light painting photography with vivid and bold colors. Shot on a professional camera medium format camera with high contrast",
    "A single comic book panel of a boy and his father on a grassy hill, staring at the sunset. A speech bubble points from the boy’s mouth says “The sun will rise again”. Muted, late 1990s coloring style.",
    "Detailed illustration of majestic lion roaring proudly in a dream-like jungle, purple white line art background, clipart on light violet paper texture",
    "A close-up portrait of a young woman with blonde hair and brown eyes. She is lying down and covering her mouth with a dark blue sweater, only her eyes are visible. The background is dark and blurry. The light is coming from above, creating shadows on her face.",
    "A mother fox playing with her baby, showing love and affection in the natural environment of their habitat. The photo captures them sharing a moment, showcasing the bond between animals. The focus is on their faces.",
    "Shot in the style of DSLR camera with the polarizing filter. A photo of three hot air balloons floating over the unique rock formations in Cappadocia, Turkey. The colors and patterns on these balloons contrast beautifully against the earthy tones of the landscape below. This shot captures the sense of adventure that comes with enjoying such an experience",
]

CRITIC_PROMPT = """
    You're a friendly visual magazine editor who loves AI generated images with Imagen 3, Google's latest image generation model whose quality exceeds all leading external competitors in aesthetics, defect-free, and text image alignment. You are always friendly and positive and not shy to provide critiques with delightfully cheeky, clever streak. You've been presented with these images for your thoughts.

    The prompt used by the author to create these images was: '{prompt}'

    Create a few sentence critique and commentary (3-4 sentences) complimenting each these images individually and together, paying special attention to quality of each image such calling out anything you notice in these following areas:
    * Alignment with prompt - how well each image mached the given text prompt
    * Photorealism - how closely the image resembles the type of image requested to be generated
    * Detail - the level of detail and overall clarity
    * Defects - any visible artifacts, distortions, or errors

    Include aesthetic qualities (come up with a score). Include commentary on color, tone, subject, lighting, and composition. You may address the author as "you."
"""


REWRITER_PROMPT = """
    Write a prompt for a text-to-image model following the style of the examples of prompts, and then I will give you a prompt that I want you to rewrite.

    Examples of prompts:

    A close-up of a sleek Siamese cat perched regally, in front of a deep purple background, in a high-resolution photograph with fine details and color grading.
    Flat vector illustration of "Breathe deep" hand-lettering with floral and leaf decorations. Bright colors, simple lines, and a cute, minimalist design on a white background.
    Long exposure photograph of rocks and sea, long shot of cloudy skies, golden hour at the rocky shore with reflections in the water. High resolution.
    Three women stand together laughing, with one woman slightly out of focus in the foreground. The sun is setting behind the women, creating a lens flare and a warm glow that highlights their hair and creates a bokeh effect in the background. The photography style is candid and captures a genuine moment of connection and happiness between friends. The warm light of golden hour lends a nostalgic and intimate feel to the image.
    A group of five friends are standing together outdoors with tall gray mountains in the background. One woman is wearing a black and white striped top and is laughing with her hand on her mouth. The man next to her is wearing a blue and green plaid shirt, khaki shorts, and a camera around his neck, he is laughing and has his arm around another man who is bent over laughing wearing a gray shirt and black pants with a camera around his neck. Behind them, a blonde woman with sunglasses on her head and wearing a beige top and red backpack is laughing and pushing the man in the gray shirt.
    An elderly woman with gray hair is sitting on a park bench next to a medium-sized brown and white dog, with the sun setting behind them, creating a warm orange glow and lens flare. She is wearing a straw sun hat and a pink patterned jacket and has a peaceful expression as she looks off into the distance.
    A woman with blonde hair wearing sunglasses stands amidst a dazzling display of golden bokeh lights. Strands of lights and crystals partially obscure her face, and her sunglasses reflect the lights. The light is low and warm creating a festive atmosphere and the bright reflections in her glasses and the bokeh. This is a lifestyle portrait with elements of fashion photography.
    A closeup of an intricate, dew-covered flower in the rain. The focus is on the delicate petals and water droplets, capturing their soft pastel colors against a dark blue background. Shot from eye level using natural light to highlight the floral texture and dew's glistening effect. This image conveys the serene beauty found within nature's miniature worlds in the style of realist details
    A closeup of a pair of worn hands, wrinkled and weathered, gently cupping a freshly baked loaf of bread. The focus is on the contrast between the rough hands and the soft dough, with flour dusting the scene. Warm light creates a sense of nourishment and tradition in the style of realistic details
    A Dalmatian dog in front of a pink background in a full body dynamic pose shot with high resolution photography and fine details isolated on a plain stock photo with color grading in the style of a hyper realistic style
    A massive spaceship floating above an industrial city, with the lights of thousands of buildings glowing in the dusk. The atmosphere is dark and mysterious, in the cyberpunk style, and cinematic
    An architectural photograph of an interior space made from interwoven, organic forms and structures inspired in the style of coral reefs and patterned textures. The scene is bathed in the warm glow of natural light, creating intricate shadows that accentuate the fluidity and harmony between the different elements within the design

    Prompt to rewrite:

    '{prompt}'

    Don’t generate images, provide only the rewritten prompt.
"""

SEMANTIC_TYPES = [
    me.SelectOption(label="Airplane", value="airplane"),
    me.SelectOption(label="Animal Other", value="animal_other"),
    me.SelectOption(label="Apple", value="apple"),
    me.SelectOption(label="Apparel", value="apparel"),
    me.SelectOption(label="Arcade Machine", value="arcade_machine"),
    me.SelectOption(label="Armchair", value="armchair"),
    me.SelectOption(label="Autorickshaw", value="autorickshaw"),
    me.SelectOption(label="Awning", value="awning"),
    me.SelectOption(label="Backpack", value="backpack"),
    me.SelectOption(label="Bag", value="bag"),
    me.SelectOption(label="Banana", value="banana"),
    me.SelectOption(label="Banner", value="banner"),
    me.SelectOption(label="Base", value="base"),
    me.SelectOption(label="Baseball Bat", value="baseball_bat"),
    me.SelectOption(label="Baseball Glove", value="baseball_glove"),
    me.SelectOption(label="Basket", value="basket"),
    me.SelectOption(label="Bathtub", value="bathtub"),
    me.SelectOption(label="Bear", value="bear"),
    me.SelectOption(label="Bed", value="bed"),
    me.SelectOption(label="Bicycle", value="bicycle"),
    me.SelectOption(label="Bicyclist", value="bicyclist"),
    me.SelectOption(label="Billboard", value="billboard"),
    me.SelectOption(label="Bike Rack", value="bike_rack"),
    me.SelectOption(label="Bird", value="bird"),
    me.SelectOption(label="Blanket", value="blanket"),
    me.SelectOption(label="Boat Ship", value="boat_ship"),
    me.SelectOption(label="Book", value="book"),
    me.SelectOption(label="Bookshelf", value="bookshelf"),
    me.SelectOption(label="Bottle", value="bottle"),
    me.SelectOption(label="Bowl", value="bowl"),
    me.SelectOption(label="Box", value="box"),
    me.SelectOption(label="Bridge", value="bridge"),
    me.SelectOption(label="Broccoli", value="broccoli"),
    me.SelectOption(label="Building", value="building"),
    me.SelectOption(label="Bulletin Board", value="bulletin_board"),
    me.SelectOption(label="Bus", value="bus"),
    me.SelectOption(label="Cabinet", value="cabinet"),
    me.SelectOption(label="Cake", value="cake"),
    me.SelectOption(label="Car", value="car"),
    me.SelectOption(label="Cabinet", value="cabinet"),
    me.SelectOption(label="Case", value="case"),
    me.SelectOption(label="Cat", value="cat"),
    me.SelectOption(label="Ceiling", value="ceiling"),
    me.SelectOption(label="Cctv Camera", value="cctv_camera"),
    me.SelectOption(label="Chair Other", value="chair_other"),
    me.SelectOption(label="Chandelier", value="chandelier"),
    me.SelectOption(label="Chest Of Drawers", value="chest_of_drawers"),
    me.SelectOption(label="Clock", value="clock"),
    me.SelectOption(label="Column", value="column"),
    me.SelectOption(label="Conveyor Belt", value="conveyor_belt"),
    me.SelectOption(label="Couch", value="couch"),
    me.SelectOption(label="Counter Other", value="counter_other"),
    me.SelectOption(label="Crib", value="crib"),
    me.SelectOption(label="Cup", value="cup"),
    me.SelectOption(label="Curtain Other", value="curtain_other"),
    me.SelectOption(label="Desk", value="desk"),
    me.SelectOption(label="Dishwasher", value="dishwasher"),
    me.SelectOption(label="Dog", value="dog"),
    me.SelectOption(label="Donut", value="donut"),
    me.SelectOption(label="Door", value="door"),
    me.SelectOption(label="Elephant", value="elephant"),
    me.SelectOption(label="Escalator", value="escalator"),
    me.SelectOption(label="Fan", value="fan"),
    me.SelectOption(label="Fence", value="fence"),
    me.SelectOption(label="Fire Hydrant", value="fire_hydrant"),
    me.SelectOption(label="Fireplace", value="fireplace"),
    me.SelectOption(label="Flag", value="flag"),
    me.SelectOption(label="Floor", value="floor"),
    me.SelectOption(label="Food Other", value="food_other"),
    me.SelectOption(label="Fork", value="fork"),
    me.SelectOption(label="Fountain", value="fountain"),
    me.SelectOption(label="Fruit Other", value="fruit_other"),
    me.SelectOption(label="Frisbee", value="frisbee"),
    me.SelectOption(label="Giraffe", value="giraffe"),
    me.SelectOption(label="Gravel", value="gravel"),
    me.SelectOption(label="Guard Rail", value="guard_rail"),
    me.SelectOption(label="Hair Dryer", value="hair_dryer"),
    me.SelectOption(label="Horse", value="horse"),
    me.SelectOption(label="Hot Dog", value="hot_dog"),
    me.SelectOption(label="Junction Box", value="junction_box"),
    me.SelectOption(label="Keyboard", value="keyboard"),
    me.SelectOption(label="Kitchen Island", value="kitchen_island"),
    me.SelectOption(label="Kite", value="kite"),
    me.SelectOption(label="Knife", value="knife"),
    me.SelectOption(label="Lamp", value="lamp"),
    me.SelectOption(label="Laptop", value="laptop"),
    me.SelectOption(label="Light Other", value="light_other"),
    me.SelectOption(label="Mailbox", value="mailbox"),
    me.SelectOption(label="Microwave", value="microwave"),
    me.SelectOption(label="Mirror", value="mirror"),
    me.SelectOption(label="Mouse", value="mouse"),
    me.SelectOption(label="Mountain Hill", value="mountain_hill"),
    me.SelectOption(label="Motorcycle", value="motorcycle"),
    me.SelectOption(label="Motorcyclist", value="motorcyclist"),
    me.SelectOption(label="Net", value="net"),
    me.SelectOption(label="Nightstand", value="nightstand"),
    me.SelectOption(label="Orange", value="orange"),
    me.SelectOption(label="Oven", value="oven"),
    me.SelectOption(label="Painting", value="painting"),
    me.SelectOption(label="Paper", value="paper"),
    me.SelectOption(label="Parking Meter", value="parking_meter"),
    me.SelectOption(label="Person", value="person"),
    me.SelectOption(label="Pier Wharf", value="pier_wharf"),
    me.SelectOption(label="Pillow", value="pillow"),
    me.SelectOption(label="Pizza", value="pizza"),
    me.SelectOption(label="Plate", value="plate"),
    me.SelectOption(label="Platform", value="platform"),
    me.SelectOption(label="Potted Plant", value="potted_plant"),
    me.SelectOption(label="Poster", value="poster"),
    me.SelectOption(label="Pool Table", value="pool_table"),
    me.SelectOption(label="Range Hood", value="range_hood"),
    me.SelectOption(label="Refrigerator", value="refrigerator"),
    me.SelectOption(label="Remote", value="remote"),
    me.SelectOption(label="Road", value="road"),
    me.SelectOption(label="Rock", value="rock"),
    me.SelectOption(label="Rug Floormat", value="rug_floormat"),
    me.SelectOption(label="Sheep", value="sheep"),
    me.SelectOption(label="Shower", value="shower"),
    me.SelectOption(label="Sink", value="sink"),
    me.SelectOption(label="Skateboard", value="skateboard"),
    me.SelectOption(label="Ski", value="ski"),
    me.SelectOption(label="Snow", value="snow"),
    me.SelectOption(label="Stage", value="stage"),
    me.SelectOption(label="Stairs", value="stairs"),
    me.SelectOption(label="Storage Tank", value="storage_tank"),
    me.SelectOption(label="Stove", value="stove"),
    me.SelectOption(label="Sunglasses", value="sunglasses"),
    me.SelectOption(label="Surfboard", value="surfboard"),
    me.SelectOption(label="Swivel Chair", value="swivel_chair"),
    me.SelectOption(label="Table", value="table"),
    me.SelectOption(label="Toilet", value="toilet"),
    me.SelectOption(label="Towel", value="towel"),
    me.SelectOption(label="Train", value="train"),
    me.SelectOption(label="Vase", value="vase"),
    me.SelectOption(label="Vegetation", value="vegetation"),
    me.SelectOption(label="Wardrobe", value="wardrobe"),
    me.SelectOption(label="Washer Dryer", value="washer_dryer"),
    me.SelectOption(label="Whiteboard", value="whiteboard"),
    me.SelectOption(label="Window", value="window"),
    me.SelectOption(label="Zebra", value="zebra"),
]
