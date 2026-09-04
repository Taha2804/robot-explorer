import asyncio
import sys
from playwright.async_api import async_playwright

# UPDATE THIS: Replace with your actual live GitHub Pages URL after deploying
HOSTED_URL = "https://taha2804.github.io/robot-explorer/"

async def main():
    target_url = sys.argv[1] if len(sys.argv) > 1 else HOSTED_URL

    async with async_playwright() as p:
        # Launch browser (headless=False allows visual verification)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Telemetry callback executed inside Python
        def handle_telemetry(state):
            x = state.get("x", 0.0)
            z = state.get("z", 0.0)
            rot = state.get("rotationY", 0.0)
            print(f"\r[Live Telemetry] X: {x:6.2f} | Z: {z:6.2f} | Yaw: {rot:5.2f} rad", end="", flush=True)

        # Expose Python callback into browser context
        await page.expose_function("onRobotStateFromBrowser", handle_telemetry)

        # Inject listener to catch window.postMessage from index.html
        await page.add_init_script("""
            window.addEventListener("message", (event) => {
                if (event.data && event.data.type === "robot-state") {
                    window.onRobotStateFromBrowser(event.data);
                }
            });
        """)

        print(f"Connecting to live hosted page: {target_url}")
        await page.goto(target_url)

        # Helper to dispatch control commands into the page
        async def send_command(forward=False, back=False, left=False, right=False, run=False):
            await page.evaluate(f"""
                window.postMessage({{
                    type: "robot-command",
                    forward: {str(forward).lower()},
                    back: {str(back).lower()},
                    left: {str(left).lower()},
                    right: {str(right).lower()},
                    run: {str(run).lower()}
                }}, "*");
            """)

        print("\n[Connected] Driving robot autonomously from local Python...\n")

        try:
            while True:
                # Drive forward while turning left
                await send_command(forward=True, left=True, run=True)
                await asyncio.sleep(2.0)

                # Move straight forward
                await send_command(forward=True, left=False, run=False)
                await asyncio.sleep(1.5)

                # Rotate right in place
                await send_command(forward=False, right=True)
                await asyncio.sleep(1.0)
        except KeyboardInterrupt:
            print("\nShutting down bridge...")
            await send_command(forward=False, back=False, left=False, right=False, run=False)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())