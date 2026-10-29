// Resolve public package entries without starting the workflow transport.
import {discoverSdk, resolvePackage} from './sdk-resolution.mjs';

const sdk = discoverSdk();
export const piSdkPackageDir = sdk.packageDir;
export const piSdk = await import(sdk.entryURL);

// Test providers must share the SDK's dependency instance, whether dependencies
// are nested, hoisted, or symlinked. Consumers never construct dist/ paths.
export function importPiDependency(specifier) {
  return import(resolvePackage(specifier, sdk.entryURL));
}
