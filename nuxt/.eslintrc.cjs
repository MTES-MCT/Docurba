module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
  },
  parserOptions: {
    parser: 'babel-eslint',
  },
  extends: ['@nuxtjs', 'plugin:nuxt/recommended'],
  plugins: [],
  // Add your custom rules here
  rules: {
    'import/no-anonymous-default-export': ['error', {
      allowArray: false,
      allowArrowFunction: false,
      allowAnonymousClass: false,
      allowAnonymousFunction: false,
      allowCallExpression: false, // Backward compatibility -> e.g. export default foo(bar)
      allowNew: false,
      allowLiteral: false,
      allowObject: true,
    }],
  },
}
